import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from db import get_entries_by_user, update_username, get_user_by_username
from auth import get_current_user
from lang import t, format_date

st.set_page_config(page_title="Aiauly", page_icon="logo.png", layout="wide")

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

    /* Стили кнопок */
    .stButton > button {
        background-color: #877BCC;
        color: white;
        border-radius: 12px;
        padding: 0.7em 1.4em;
        font-weight: 600;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #C3BDE5;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }

    .button-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 40px 0;
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

    # Кнопка "Главная" в sidebar
    if st.sidebar.button(t("home"), key="main_btn"):
        st.switch_page("pages/diary.py")

    if st.sidebar.button(t("selfcare_page"), key="selfcare_btn"):
        st.switch_page("pages/selfcare_page.py")

    # Logout button in sidebar
    if st.sidebar.button(t("logout"), key="logout_btn"):
        if "user" in st.session_state:
            del st.session_state["user"]
        st.switch_page("main.py")


# --- Заголовок профиля ---
# Используем сессию для динамического обновления username
if "display_username" not in st.session_state:
    st.session_state["display_username"] = user["username"]

st.markdown(f"""
    <div style="text-align:center; padding:20px;">
        <h2 style="margin-bottom:5px;">👤 {st.session_state['display_username']}</h2>
        <p style="color:gray; margin-top:0;">{user['email']}</p>
    </div>
""", unsafe_allow_html=True)

# --- Изменение username ---
new_username = st.text_input(t("change_username"), value=st.session_state.get("display_username", user["username"]))
if st.button(t("save_username")):
    if not new_username.strip():
        st.warning(t("empty_username"))
    else:
        # Проверяем, занят ли уже такой username
        existing_user = get_user_by_username(new_username.strip())
        if existing_user and existing_user["id"] != user_id:
            st.warning(t("username_exists"))
        else:
            update_username(user_id, new_username.strip())
            # Обновляем отображаемое имя сразу на странице
            st.session_state["display_username"] = new_username.strip()
            st.success(t("updated_username"))

st.markdown("---")

# --- Фильтр по периодам ---
period_options = t("filter_periods")
period = st.radio(t("show_entries_for"), period_options, horizontal=True)

# Сопоставление с числом дней
days_map = {
    period_options[0]: 7,
    period_options[1]: 14,
    period_options[2]: 30
}
days = days_map[period]

entries = get_entries_by_user(user_id)

if entries:
    df = pd.DataFrame(entries)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date", ascending=False)
    cutoff = datetime.now().date() - timedelta(days=days)
    df = df[df["date"].dt.date >= cutoff]

    if df.empty:
        st.info(t("no_entries_period"))
    else:
        for _, row in df.iterrows():
            color = {"positive": "#d4f7d4", "neutral": "#fff5ba", "negative": "#ffcccc"}.get(row["sentiment"], "#ffffff")
            
            # --- Используем format_date для красивой даты и убираем лишние нули ---
            formatted_date = format_date(row["date"].to_pydatetime(), st.session_state["language"], full=True)
            formatted_time = row["time"][:5]  # HH:MM
            
            st.markdown(f"""
            <div style="background-color:{color}; padding:15px; border-radius:12px; margin-bottom:15px;
                        box-shadow:0 4px 15px rgba(0,0,0,0.1);">
                <p style="font-size:16px; margin-bottom:10px;">{row['text']}</p>
                <p style="font-size:12px; color:gray;">{formatted_date} {formatted_time}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info(t("no_entries_period"))

st.markdown("---")
st.write("© 2025 Aiauly")

# Privacy Policy
with st.expander("🔒 Privacy Policy"):
    st.write("""
    This Privacy Policy explains how Aiauly collects, uses, and protects your information.
    
    - We collect minimal data (email, username, mood entries) only for the functionality of the app.  
    - Your data is stored securely in Supabase.  
    - We do not share your information with third parties. 
    
    Please review this policy regularly for updates.
    """)

# Terms of Service
with st.expander("📜 Terms of Service"):
    st.write("""
    By using Aiauly, you agree to the following terms:
    
    1. This is not a medical or psychological service.  
    2. The app is for personal self-care and mood tracking only.  
    3. We are not responsible for decisions you make based on AI analysis.  
    4. You agree not to misuse the service or share inappropriate content.  
    
    Continued use of the app means you accept these terms.
    """)

# Help
with st.expander("❓ Help"):
    st.write("""
    **How to use Aiauly:**
    1. Register or log in to your personal account to start tracking your mood.
    2. Write your daily thoughts or feelings in the text box.
    3. Click **Analyze** to get AI feedback and helpful recommendations.
    4. View your mood trends and insights on the charts.

    **Forgot your password?**
    - Currently, password recovery is not available.  
    - If you forgot your login details, please create a new account with a different email.  
    - Keep your login info safe for future use.

    **Need more help?**
    - For questions or support, contact us at: **support@aiauly.app**
    - Check out the **Privacy Policy** and **Terms of Service** for additional info.
    """)

# About
with st.expander("ℹ️ About"):
    st.write("""
    **Aiauly** is an AI-powered mood diary designed to help people 
    reflect on their emotions, track trends, and receive self-care advice.  
    
    - Project created in 2025  
    - Founder: Aiaulym Oishy  
    - Mission: To support mental well-being and self-reflection  
    
    Thank you for using Aiauly 💜
    """)