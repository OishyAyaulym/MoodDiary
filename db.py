import streamlit as st
from supabase import create_client
from typing import Optional
import pandas as pd
from datetime import date, time, timedelta

# --- Подключение к Supabase через Service Role для таблицы users ---
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
supabase_service = create_client(url, key)

# --- USERS ---
def create_user(username: str, email: str, user_id: str):
    response = supabase_service.table("users").insert({
        "id": user_id,
        "username": username,
        "email": email
    }).execute()
    return response

def get_user_by_email(email: str) -> Optional[dict]:
    response = supabase_service.table("users").select("*").eq("email", email).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def get_user_by_username(username: str) -> Optional[dict]:
    response = supabase_service.table("users").select("*").eq("username", username).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def update_username(user_id: str, new_username: str):
    response = supabase_service.table("users").update({"username": new_username}).eq("id", user_id).execute()
    return response

# --- ENTRIES (Mood Logs) ---
def save_entry(user_id: str, text: str, sentiment: str, entry_date: date, entry_time: time):
    response = supabase_service.table("entries").insert({
        "user_id": user_id,
        "text": text,
        "sentiment": sentiment,
        "date": entry_date.isoformat(),
        "time": entry_time.strftime('%H:%M:%S')
    }).execute()
    return response

def get_entries_by_user(user_id: str):
    response = supabase_service.table("entries").select("*").eq("user_id", user_id).order("date").execute()
    return response.data

def get_user_moods(user_id: str) -> pd.DataFrame:
    response = supabase_service.table("entries").select("*").eq("user_id", user_id).order("date").execute()
    if not response.data:
        return pd.DataFrame(columns=["id", "user_id", "date", "text", "sentiment"])
    df = pd.DataFrame(response.data)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

# --- USER ANXIETY ACTIONS ---
def save_user_anxiety_action(user_id: str, action: str, action_date: date):
    response = supabase_service.table("user_anxiety_actions").insert({
        "user_id": user_id,
        "action_taken": action,
        "date": action_date.isoformat()
    }).execute()
    return response

def check_user_anxiety_action(user_id: str, action_date: date) -> bool:
    response = supabase_service.table("user_anxiety_actions").select("*") \
        .eq("user_id", user_id).eq("date", action_date.isoformat()).execute()
    return bool(response.data)

def get_user_anxiety_actions(user_id: str, start_date: date, end_date: date):
    response = supabase_service.table("user_anxiety_actions").select("*") \
        .eq("user_id", user_id) \
        .gte("date", start_date.isoformat()) \
        .lte("date", end_date.isoformat()) \
        .order("date", ascending=True).execute()
    return response.data

def check_anxiety_alert(user_id: str, days: int = 7, negative_days_threshold: int = 4):
    """
    Проверяет, нужно ли показывать тревожку пользователю.

    :param user_id: ID пользователя
    :param days: за сколько последних дней проверяем
    :param negative_days_threshold: сколько негативных дней нужно для тревожки
    :return: (alert_needed: bool, negative_days_count: int)
    """
    today = date.today()
    start_date = today - timedelta(days=days)

    # Получаем записи пользователя
    user_moods = get_user_moods(user_id)
    if user_moods.empty:
        return False, 0

    # Приводим даты к datetime.date
    user_moods["date"] = pd.to_datetime(user_moods["date"]).dt.date

    # Фильтруем последние N дней
    recent_entries = user_moods[(user_moods["date"] >= start_date) & (user_moods["date"] <= today)]

    # Считаем негативные дни
    negative_entries = recent_entries[recent_entries["sentiment"] == "negative"]
    negative_days_count = negative_entries["date"].nunique()

    # Проверяем, делал ли пользователь уже действие сегодня
    action_today_done = check_user_anxiety_action(user_id, today)

    # Нужно ли показывать тревожку
    alert_needed = negative_days_count > negative_days_threshold and not action_today_done

    return alert_needed, negative_days_count

def get_last_entries(user_id: str, n: int = 7):
    response = supabase_service.table("entries").select("*") \
        .eq("user_id", user_id).order("date", desc=True).limit(n).execute()
    return response.data or []