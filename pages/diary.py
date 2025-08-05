import streamlit as st
from datetime import datetime
import pandas as pd
from mood_analysis import classify_sentiment_for_csv, generate_support_and_advice
from plot import plot_interactive_sentiment
from db import save_entry, get_entries_by_user
from auth import get_current_user


user = get_current_user()

if not user:
    st.warning("Пожалуйста, войдите или зарегистрируйтесь.")
    st.stop()

user_id = user["id"]
st.success(f"Привет, {user['username']}! 👋")

# --- Название и подзаголовок ---
st.markdown("""
    <style>
    .gradient-text {
        font-size: 20px;
        font-weight: bold;
        background: linear-gradient(135deg, #00F5A0, #00D9F5, #3E00F5, #FF00C8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
    <h1 class="gradient-text">Дневник настроения</h1>
""", unsafe_allow_html=True)
st.markdown("<h3 style='color: #717171 ;'>Отслеживайте свои эмоции с помощью искусственного интеллекта🌞</h3>", unsafe_allow_html=True)
st.markdown("---")

# --- Выбор языка ---
language = st.selectbox(
    "🌐 Select language / Тілді таңдаңыз / Выберите язык",
    options=["ru", "kk", "en"],
    format_func=lambda x: {"ru": "Русский", "kk": "Қазақша", "en": "English"}[x]
)

# --- Ввод текста ---
user_input = st.text_area("Как прошел ваш день? Что вы чувствуете?")

if st.button("Проанализировать"):
    if not user_input.strip():
        st.warning("Пожалуйста, введите текст.")
    else:
        with st.spinner("Анализируем настроение..."):
            sentiment = classify_sentiment_for_csv(user_input)
            now = datetime.now()
            save_entry(user_id, user_input, sentiment, now.date(), now.time())

            support_response = generate_support_and_advice(user_input, language)
            st.markdown(support_response)

# --- График ---
entries = get_entries_by_user(user_id)
if entries:
    df = pd.DataFrame(entries)
else:
    df = pd.DataFrame(columns=["user_id", "text", "sentiment", "date", "time"])
plot_interactive_sentiment(df, lang=language)