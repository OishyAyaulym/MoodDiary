from openai import OpenAI
from datetime import datetime
import pandas as pd
import streamlit as st
from db import save_entry, get_entries_by_user

client = OpenAI(api_key=st.secrets["openai_key"])


# --- Загрузка модели сентимент-анализа ---
@st.cache_resource(show_spinner=False)
def classify_sentiment_for_csv(text):
    """Возвращает: one of ['negative', 'neutral', 'positive']"""
    prompt = f"""
Determine the emotional tone of the following message. Respond with one word only — either: negative, neutral, or positive. Do not add explanations.

Message: {text}
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that classifies emotional tone from a user's message."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    sentiment = response.choices[0].message.content.strip().lower()

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

Сначала скажи: "Ваше настроение: [позитивное/нейтральное/негативное]", затем напиши от 5 до 10 поддерживающих фраз и полезные советы.
""",
        "kk": f"""
Сен — қамқор эмоционалды көмекшісің. Мына мәтін негізінде:

\"{text}\"

Басында: "Сіздің көңіл-күйіңіз: [позитивті/бейтарап/негативті]" деп айт. Сосын 5–тен 10-ға дейін нақты, қарапайым және мейірімді қолдау сөздер мен пайдалы кеңес бер. Күрделі немесе ақылға қонымсыз сөйлемдерді қолданба.
""",
        "en": f"""
You are a supportive emotional assistant. Based on this text:

\"{text}\"

Start with: "Your mood is: [positive/neutral/negative]", then write from 5 to 10 encouraging phrases and helpful piece of advice.
"""
    }

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompts[lang]}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()
