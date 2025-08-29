import json
import streamlit as st
from datetime import datetime

# --- Загрузка переводов интерфейса ---
def load_translations():
    with open("translations.json", "r", encoding="utf-8") as f:
        return json.load(f)

translations = load_translations()

def t(key, **kwargs):
    lang = st.session_state.get("language", "ru")
    text = translations[lang].get(key, key)
    if isinstance(text, str):
        return text.format(**kwargs) if kwargs else text
    return text

# --- Загрузка цитат ---
def load_quotes():
    with open("quotes.json", "r", encoding="utf-8") as f:
        return json.load(f)

quotes = load_quotes()

# --- Функция: Цитата дня ---
def get_quote_of_the_day(lang="ru"):
    today_index = datetime.now().timetuple().tm_yday % len(quotes[lang])
    return quotes[lang][today_index]

def format_date(date, lang="ru", full=True):
    """
    Форматирует дату для отображения:
    full=True -> "Sunday, 17 August"
    """
    day_index = date.weekday()  # 0=Monday ... 6=Sunday
    month_index = date.month - 1

    day_name = translations[lang]["full_days"][day_index]
    month_name = translations[lang]["months"][month_index]
    day_num = date.day

    return f"{day_name}, {day_num} {month_name}"

# --- Загрузка комментариев недели ---
def load_weekly_comments():
    with open("weekly_comments.json", "r", encoding="utf-8") as f:
        return json.load(f)

weekly_comments_data = load_weekly_comments()

def get_weekly_comment(positive_days, neutral_days, negative_days, lang="ru"):
    # Определяем настроение недели
    if positive_days >= max(neutral_days, negative_days):
        mood = "positive"
    elif negative_days >= max(positive_days, neutral_days):
        mood = "negative"
    else:
        mood = "neutral"

    comment_list = weekly_comments_data[mood]

    # Индекс дня года для ежедневного обновления
    day_index = datetime.now().timetuple().tm_yday % len(comment_list)

    return comment_list[day_index][lang]