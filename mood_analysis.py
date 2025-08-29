from datetime import datetime, date, timedelta
import pandas as pd
import streamlit as st
from db import save_entry, get_entries_by_user
import google.generativeai as genai

genai.configure(api_key=st.secrets["gemini_key"])
model=genai.GenerativeModel("gemini-2.0-flash")

# --- Загрузка модели сентимент-анализа ---
@st.cache_resource(show_spinner=False)
def classify_sentiment_for_csv(text):
    """Возвращает: one of ['negative', 'neutral', 'positive']"""
    prompt = f"""
Determine the emotional tone of the following message. Respond with one word only — either: negative, neutral, or positive. Do not add explanations.

Message: {text}
"""
    response=model.generate_content(prompt)
    sentiment = response.text.strip().lower()

    # Чистим от лишнего (на всякий случай)
    if "positive" in sentiment:
        return "positive"
    elif "neutral" in sentiment:
        return "neutral"
    elif "negative" in sentiment:
        return "negative"
    else:
        return "neutral"  # безопасное значение по умолчанию


def generate_support_and_advice(text, lang="ru"):
    prompts = {
        "ru": f"""
Ты — заботливый эмоциональный помощник. На основе следующего текста:

\"{text}\"

Сначала скажи: "Ваше настроение: [позитивное/нейтральное/негативное]", затем напиши 5 поддерживающих фраз и полезные советы, каждый максимум по 1 предложению.
""",
        "kk": f"""
Сен — қамқор эмоционалды көмекшісің. Мына мәтін негізінде:

\"{text}\"

Басында: "Сіздің көңіл-күйіңіз: [позитивті/бейтарап/негативті]" деп айт. Сосын 5 нақты, қарапайым және мейірімді қолдау сөздер мен пайдалы кеңес бер, әрқайсысы 1 сөйлемнен.
""",
        "en": f"""
You are a supportive emotional assistant. Based on this text:

\"{text}\"

Start with: "Your mood is: [positive/neutral/negative]", then write 5 encouraging phrases and helpful piece of advice, each maximum 1 sentence.
"""
    }

    response=model.generate_content(prompts[lang])
    return response.text.strip()