import streamlit as st
import time
from datetime import date, timedelta
from db import save_user_anxiety_action, check_anxiety_alert
from lang import t
from auth import get_current_user

st.set_page_config(page_title="Aiauly", page_icon="logo.png", layout="wide")

user = get_current_user()
if not user:
    st.warning(t("please_login_register"))
    st.switch_page("main.py")

user_id = user["id"]

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #ff9a9e, #fad0c4, #a1c4fd);
        background-size: 400% 400%;
        animation: gradientBG 20s ease infinite;
    }
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .css-18e3th9 {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
        padding: 1rem;
    }
    header, .css-1v3fvcr {
        background-color: rgba(255,255,255,0.9);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background-color: #877BCC;
        color: white;
        border-radius: 12px;
        padding: 0.7em 1.4em;
        font-weight: 600;
        border: none;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #C3BDE5;
        transform: translateY(-2px);
    }

    /* --- Новый стиль для компактных инпутов --- */
    .compact-input input {
        margin-bottom: 6px !important;   /* уменьшенный отступ */
        padding: 6px 10px !important;    /* компактнее */
        border-radius: 8px !important;   /* закругление */
    }
    .compact-label {
        margin-bottom: 2px;
        font-size: 0.9rem;
        color: #333;
        font-weight: 500;
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

    # --- Sidebar ---
    lang_labels = {"ru": "Русский", "kk": "Қазақша", "en": "English"}
    selected_label = st.sidebar.radio(
        "",
        list(lang_labels.values()),
        index=list(lang_labels.keys()).index(st.session_state["language"])
    )
    st.session_state["language"] = list(lang_labels.keys())[list(lang_labels.values()).index(selected_label)]

    if st.sidebar.button(t("home"), key="main_btn"):
        st.switch_page("pages/diary.py")

    if st.sidebar.button(t("your_account"), key="account_btn"):
        st.switch_page("pages/user_page.py")

    if st.sidebar.button(t("logout"), key="logout_btn"):
        if "user" in st.session_state:
            del st.session_state["user"]
        st.switch_page("main.py")

# --- Заголовок ---
st.markdown("<h2 style='text-align:center;'>🌿 " + t("selfcare_title") + "</h2>", unsafe_allow_html=True)
st.markdown("---")

# --- Список интерактивных упражнений ---
exercises = [
    {"title": "1. 🌬️ " + t("one_minute_meditation"), "description": t("one_minute_meditation_desc")},
    {"title": "2. ✋ " + t("five_senses_exercise"), "description": t("five_senses_exercise_desc")},
    {"title": "3. ❤️‍🩹 " + t("gratitude_journal"), "description": t("gratitude_journal_desc")},
    {"title": "4. 🫁 " + t("breathing_478"), "description": t("breathing_478_desc")},
    {"title": "5. 🪞 " + t("positive_affirmation"), "description": t("positive_affirmation_desc")},
]

# --- Состояние выполнения упражнений ---
if "exercise_done" not in st.session_state:
    st.session_state["exercise_done"] = {i: False for i in range(len(exercises))}

st.markdown("### " + t("instructions_exercises"))

for i, ex in enumerate(exercises):
    st.markdown(f"**{ex['title']}**")
    st.markdown(f"{ex['description']}")

    # --- Упражнение 1: Медитация с обратным отсчетом ---
    if i == 0:
        if not st.session_state["exercise_done"][i]:
            if st.button(t("start_meditation"), key=f"start_{i}"):
                countdown_placeholder = st.empty()
                for sec in range(60, 0, -1):
                    countdown_placeholder.markdown(f"⏳ {sec} s...")
                    time.sleep(1)
                st.session_state[f"ready_done_{i}"] = True  # флаг готовности кнопки
        if st.session_state.get(f"ready_done_{i}", False):
            if st.button(t("mark_done"), key=f"done_{i}"):
                st.session_state["exercise_done"][i] = True
        if st.session_state["exercise_done"][i]:
            st.success("✅ " + t("exercise_completed"))

    # --- Упражнение 2: 5-4-3-2-1 ---
    elif i == 1:
        five_prompts = [
            t("five_senses_see"),
            t("five_senses_hear"),
            t("five_senses_feel"),
            t("five_senses_smell"),
            t("five_senses_taste"),
        ]
        five_inputs = []
        for j, prompt in enumerate(five_prompts):
            st.markdown(f"<div class='compact-label'>{prompt}</div>", unsafe_allow_html=True)
            five_inputs.append(st.text_input("", key=f"five_{j}", label_visibility="collapsed", placeholder="...", help=prompt))

        if not st.session_state["exercise_done"][i]:
            if st.button(t("mark_done"), key=f"done_{i}"):
                if all(five_inputs):
                    st.session_state["exercise_done"][i] = True
                    st.success(t("exercise_completed"))
                else:
                    st.warning(t("fill_all_fields"))
        else:
            st.success("✅ " + t("exercise_completed"))

    # --- Упражнение 3: Дневник благодарности ---
    elif i == 2:
        gratitude_prompts = [t("gratitude_1"), t("gratitude_2"), t("gratitude_3")]
        gratitude_inputs = []
        for j, prompt in enumerate(gratitude_prompts):
            st.markdown(f"<div class='compact-label'>{prompt}</div>", unsafe_allow_html=True)
            gratitude_inputs.append(st.text_input("", key=f"grat_{j}", label_visibility="collapsed", placeholder="..."))

        if not st.session_state["exercise_done"][i]:
            if st.button(t("mark_done"), key=f"done_{i}"):
                if all(gratitude_inputs):
                    st.session_state["exercise_done"][i] = True
                    st.success(t("exercise_completed"))
                else:
                    st.warning(t("fill_all_fields"))
        else:
            st.success("✅ " + t("exercise_completed"))

    # --- Упражнение 4: Дыхание 4-7-8 ---
    elif i == 3:
        if not st.session_state["exercise_done"][i]:
            if st.button(t("start_breathing"), key=f"start_{i}"):
                breathing_placeholder = st.empty()
                for cycle in range(1, 4):
                    breathing_placeholder.markdown(f"🌬️ {cycle}/3 – {t('inhale')} 4s")
                    time.sleep(4)
                    breathing_placeholder.markdown(f"😌 {cycle}/3 – {t('hold')} 7s")
                    time.sleep(7)
                    breathing_placeholder.markdown(f"🕊️ {cycle}/3 – {t('exhale')} 8s")
                    time.sleep(8)
                st.session_state[f"ready_done_{i}"] = True
        if st.session_state.get(f"ready_done_{i}", False):
            if st.button(t("mark_done"), key=f"done_{i}"):
                st.session_state["exercise_done"][i] = True
        if st.session_state["exercise_done"][i]:
            st.success("✅ " + t("exercise_completed"))

    # --- Упражнение 5: Позитивная аффирмация ---
    elif i == 4:
        affirmation = st.text_input(t("affirmation_prompt"), key="affirmation_input")
        if not st.session_state["exercise_done"][i]:
            if st.button(t("mark_done"), key=f"done_{i}"):
                if affirmation:
                    st.session_state["exercise_done"][i] = True
                    st.success("✅ " + t("exercise_completed"))
                else:
                    st.warning(t("fill_all_fields"))
        else:
            st.success("✅ " + t("exercise_completed"))

st.markdown("---")

# --- Блок рекомендации психологического центра ---
alert_needed, negative_days_count = check_anxiety_alert(user_id, days=7, negative_days_threshold=4)

if alert_needed:
    block_color = "rgba(255, 75, 75, 0.85)"  # мягкий красный
    text_color = "white"
else:
    block_color = "rgba(240, 240, 240, 0.9)"  # светло-серый
    text_color = "black"

st.markdown(f"""
    <div style='background-color:{block_color}; 
                padding:20px; 
                border-radius:12px; 
                color:{text_color};
                font-weight:normal; 
                text-align:center; 
                margin-top:20px;
                margin-bottom:20px;'>
        {t("anxiety_recommend_psych_center")}
    </div>
""", unsafe_allow_html=True)


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