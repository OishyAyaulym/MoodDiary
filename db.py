import streamlit as st
from supabase import create_client
from typing import Optional
from datetime import date, time

# Подключение к Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

# ========== USERS ==========

def create_user(username: str, email: str, password_hash: str):
    response = supabase.table("users").insert({
        "username": username,
        "email": email,
        "password": password_hash
    }).execute()
    return response

def get_user_by_email(email: str) -> Optional[dict]:
    response = supabase.table("users").select("*").eq("email", email).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

def get_user_by_username(username: str) -> Optional[dict]:
    response = supabase.table("users").select("*").eq("username", username).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return None

# ========== ENTRIES (MOOD LOGS) ==========

def save_entry(user_id: str, text: str, sentiment: str, entry_date: date, entry_time: time):
    response = supabase.table("entries").insert({
        "user_id": user_id,
        "text": text,
        "sentiment": sentiment,
        "date": entry_date.isoformat(),  # формат YYYY-MM-DD
        "time": entry_time.strftime('%H:%M:%S')  # формат HH:MM:SS
    }).execute()
    return response

def get_entries_by_user(user_id: str):
    response = supabase.table("entries").select("*").eq("user_id", user_id).order("date").execute()
    return response.data
