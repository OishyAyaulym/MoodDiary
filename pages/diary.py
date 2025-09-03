import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
from mood_analysis import classify_sentiment_for_csv, generate_support_and_advice
from plot import plot_interactive_sentiment, analyze_weekly_mood
from db import save_entry, get_entries_by_user, save_user_anxiety_action, check_anxiety_alert
from auth import get_current_user
from lang import t, get_quote_of_the_day, format_date, get_weekly_comment

st.set_page_config(page_title="Aiauly", page_icon="logo.png", layout="wide")

if "language" not in st.session_state:
    st.session_state["language"] = "ru"

user = get_current_user()

if not user:
    st.warning(t("please_login_register"))
    st.switch_page("main.py")

user_id = user["id"]

st.markdown(
    """
    <style>
    /* Градиент фона на весь Streamlit-контейнер */
    .stApp {
        background: linear-gradient(135deg, #ff9a9e, #fad0c4, #a1c4fd);
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
        transition: background 0.5s ease;
    }

    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    /* Прозрачный фон у блоков */
    .css-18e3th9 {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        padding: 1rem;
        transition: all 0.3s ease;
    }

    /* Прозрачная верхняя панель */
    header, .css-1v3fvcr {
        background-color: rgba(255,255,255,0.9);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Общий стиль для кнопок */
    div.stButton > button, 
    div.stButton button, 
    .stButton button[kind="primary"], 
    .stButton button[kind="secondary"] {
        background-color: #877BCC;
        color: white;
        border-radius: 12px;
        padding: 0.7em 1.4em;
        font-weight: 600;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        width: 100% !important;   /* фикс на деплой */
        display: block;           /* чтобы растягивалось */
    }

    /* Hover эффект */
    div.stButton > button:hover, 
    .stButton button:hover {
        background-color: #C3BDE5;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown(f"""
    <style>
    .gradient-text {{
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        background: linear-gradient(135deg, #6654C7, #9487DA, #9E8DDA, #A893DA, #B79CDB, #BC9FDB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    </style>
    <h1 class="gradient-text">{t('app_name')}</h1>
    """, unsafe_allow_html=True)

    # Header with user info and logout
    lang_labels = {"ru": "Русский", "kk": "Қазақша", "en": "English"}
    selected_label = st.sidebar.radio(
        "",
        list(lang_labels.values()),
        index=list(lang_labels.keys()).index(st.session_state["language"])
    )
    st.session_state["language"] = list(lang_labels.keys())[list(lang_labels.values()).index(selected_label)]

    # Кнопка "Ваш аккаунт" в sidebar
    if st.sidebar.button(t("your_account"), key="account_btn"):
        st.switch_page("pages/user_page.py")

    if st.sidebar.button(t("selfcare_page"), key="selfcare_btn"):
        st.switch_page("pages/selfcare_page.py")

    # Logout button in sidebar
    if st.sidebar.button(t("logout"), key="logout_btn"):
        if "user" in st.session_state:
            del st.session_state["user"]
        st.switch_page("main.py")

alert_needed, negative_days_count = check_anxiety_alert(user_id, days=7, negative_days_threshold=4)

if alert_needed:
    st.markdown(f"""
        <div style='background-color: rgba(255, 75, 75, 0.85); 
                    padding:20px; 
                    border-radius:12px; 
                    color:white; 
                    font-weight:normal; 
                    text-align:center; 
                    margin-bottom:20px;'>
            {t("anxiety_alert_message")}
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("go_to_selfcare")):
            save_user_anxiety_action(user_id, "selfcare", date.today())
            st.switch_page("pages/selfcare_page.py")
    with col2:
        if st.button(t("dismiss_alert")):
            save_user_anxiety_action(user_id, "cancel", date.today())
            st.rerun()


# --- Название и подзаголовок ---
st.markdown(f"""
    <style>
    .gradient-font {{
        text-align: left;
        font-size: 40px;
        font-weight: bold;
        background: linear-gradient(135deg, #6654C7, #9487DA, #9E8DDA, #A893DA, #B79CDB, #BC9FDB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    </style>
    <h2 class="gradient-font">{t("greeting_user", username=user["username"])}</h2>
""", unsafe_allow_html=True)
st.markdown(f"<h4>{t('diary_subtitle')}</h4>", unsafe_allow_html=True)
st.markdown("---")

st.subheader("🌸 " + t("quote_of_the_day"))
quote = get_quote_of_the_day(st.session_state["language"])
st.markdown(
    f"""
    <div style='
        padding:15px; 
        border-radius:12px; 
        background:linear-gradient(90deg, #a18cd1, #fbc2eb); 
        font-style:italic; 
        font-size:18px; 
        text-align:center; 
        color:#ffffff; 
        box-shadow:0 4px 20px rgba(0,0,0,0.15);
    '>
        {quote}
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# --- Ввод текста ---
user_input = st.text_area(t("textarea_placeholder"), height=150, placeholder="...")

if st.button(t("analyze"), use_container_width=True):
    if not user_input.strip():
        st.warning(t("please_enter_text"))
    else:
        with st.spinner(t("analyzing")):
            sentiment = classify_sentiment_for_csv(user_input)
            now = datetime.now()
            save_entry(user_id, user_input, sentiment, now.date(), now.time())

            support_response = generate_support_and_advice(user_input, st.session_state["language"])
            st.markdown(support_response)

# --- Цитата дня ---
st.markdown("---")


# --- График ---
entries = get_entries_by_user(user_id)
if entries:
    df = pd.DataFrame(entries)
else:
    df = pd.DataFrame(columns=["user_id", "text", "sentiment", "date", "time"])
plot_interactive_sentiment(df)

avg_mood, best_day, worst_day, positive_days, neutral_days, negative_days = analyze_weekly_mood(df)

st.subheader(t("analysis_title"))

if avg_mood is None:
    st.info(t("no_entries"))
else:
    # Определяем текст и цвет по шкале
    if 0 <= avg_mood <= 1:
        avg_text, color = t("avg_moods")["bad"], "#FF4B4B"
    elif 1 < avg_mood <= 2:
        avg_text, color = t("avg_moods")["normal"], "#FFA500"
    elif 2 < avg_mood <= 3:
        avg_text, color = t("avg_moods")["good"], "#FFD700"
    else:  # 3 < avg_mood <= 4
        avg_text, color = t("avg_moods")["excellent"], "#4BC500"

    # --- Среднее настроение за неделю ---
    st.markdown(f"""
    <div style="background-color: rgba(255,255,255,0.85); padding:20px; border-radius:12px; 
                text-align:center; font-size:20px; font-weight:600; color:{color}; 
                margin-bottom:20px; box-shadow:0 4px 15px rgba(0,0,0,0.1);">
        {t("avg_mood_title")}<br>
        <span style="font-size:26px;">{avg_text}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # --- Лучший день ---
    with col1:
        st.markdown(f"""
        <div style="background-color: rgba(255,255,255,0.85); padding:15px; border-radius:12px; 
                    text-align:center; font-size:18px; font-weight:600; color:green; 
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            {t("best_day")}<br>
            <span style="font-size:16px; font-weight:400;">
                {format_date(best_day, st.session_state["language"], full=True)}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # --- Сложный день ---
    with col2:
        st.markdown(f"""
        <div style="background-color: rgba(255,255,255,0.85); padding:15px; border-radius:12px; 
                    text-align:center; font-size:18px; font-weight:600; color:red; 
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            {t("worst_day")}<br>
            <span style="font-size:16px; font-weight:400;">
                {format_date(worst_day, st.session_state["language"], full=True)}
            </span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4, col5 = st.columns(3)

     # Позитивные
    with col3:
        st.markdown(f"""
        <div style="background-color: rgba(76, 175, 80, 0.85); padding:15px; border-radius:12px; 
                    text-align:center; font-size:18px; font-weight:600; color:white; 
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            {t("positive_days")}<br>
            <span style="font-size:20px; font-weight:700;">{positive_days}</span>
        </div>
        """, unsafe_allow_html=True)

    # Нейтральные
    with col4:
        st.markdown(f"""
        <div style="background-color: rgba(255, 235, 59, 0.85); padding:15px; border-radius:12px; 
                    text-align:center; font-size:18px; font-weight:600; color:black; 
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            {t("neutral_days")}<br>
            <span style="font-size:20px; font-weight:700;">{neutral_days}</span>
        </div>
        """, unsafe_allow_html=True)

    # Негативные
    with col5:
        st.markdown(f"""
        <div style="background-color: rgba(244, 67, 54, 0.85); padding:15px; border-radius:12px; 
                    text-align:center; font-size:18px; font-weight:600; color:white; 
                    box-shadow:0 4px 15px rgba(0,0,0,0.1);">
            {t("negative_days")}<br>
            <span style="font-size:20px; font-weight:700;">{negative_days}</span>
        </div>
        """, unsafe_allow_html=True)

    comment_text = get_weekly_comment(positive_days, neutral_days, negative_days, lang=st.session_state["language"])

    st.markdown(f"""
    <div style="background-color: rgba(255,255,255,0.85); padding:20px; border-radius:12px; 
                text-align:center; font-size:18px; font-weight:500; color:#333; 
                margin-top:15px; margin-bottom:25px; box-shadow:0 4px 15px rgba(0,0,0,0.1);">
        {comment_text}
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.write("© 2025 Aiauly")

# Privacy Policy
with st.expander(t("privacy_policy")):
    st.write(t("privacy_policy_text"))

# Terms of Service
with st.expander(t("terms_of_service")):
    st.write(t("terms_of_service_text"))

# Help
with st.expander(t("help")):
    st.write(t("help_text"))

# About
with st.expander(t("about")):
    st.write(t("about_text"))