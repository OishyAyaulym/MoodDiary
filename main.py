import streamlit as st
from auth import signup_user, login_user
from lang import t

st.set_page_config(page_title="Aiauly", page_icon="logo.png", layout="centered")

# Сначала добавляем кастомную навигационную панель с логотипом
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
    """,
    unsafe_allow_html=True
)


# Initialize session state
if "language" not in st.session_state:
    st.session_state["language"] = "ru"
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "landing"
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"

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
    
    # Language selector (top of page)
    lang_labels = {"ru": "Русский", "kk": "Қазақша", "en": "English"}
    selected_label = st.sidebar.radio(
        "",
        list(lang_labels.values()),
        index=list(lang_labels.keys()).index(st.session_state["language"])
    )
    # Update session_state["language"] according to selection
    st.session_state["language"] = list(lang_labels.keys())[list(lang_labels.values()).index(selected_label)]

#Check if user is already authenticated
if "user" in st.session_state and st.session_state["user"]:
    st.switch_page("pages/diary.py")

# Navigation logic
if st.session_state["current_page"] == "auth":
    # Show authentication page
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
    #st.markdown(f"<h1 class='aiauly-title'>{t('app_name')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{t('please_login_register')}</p>", unsafe_allow_html=True)
    
    #Back button
    if st.button(t("back_main")):
        st.session_state["current_page"]="landing"
        st.rerun()

    # Mode switching
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("register"), key="switch_to_register"):
            st.session_state["auth_mode"] = "register"
            st.rerun()
    with col2:
        if st.button(t("login"), key="switch_to_login"):
            st.session_state["auth_mode"] = "login"
            st.rerun()
    
    # Authentication form
    mode = st.session_state["auth_mode"]
    with st.form("auth_form"):
        email = st.text_input(t("email"), key="email_input")
        if mode == "register":
            username = st.text_input(t("username"), key="username_input")
        password = st.text_input(t("password"), type="password", key="password_input")
        submitted = st.form_submit_button(t("register") if mode == "register" else t("login"))
        
        if submitted:
            if mode == "register":
                if signup_user(username, email, password):
                    st.success(t("success_register"))
                    if login_user(email, password):
                        st.rerun()
            else:
                if login_user(email, password):
                    st.success(t("success_login"))
                    st.rerun()
    
    # Bottom links
    if mode == "register":
        if st.button(t("already_have_account"), key="to_login"):
            st.session_state["auth_mode"] = "login"
            st.rerun()
    else:
        if st.button(t("no_account"), key="to_register"):
            st.session_state["auth_mode"] = "register"
            st.rerun()

else:
    # Show landing page
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
    #st.markdown(f"<h1 class='aiauly-title'>{t('app_name')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{t('welcome_text')}</p>", unsafe_allow_html=True)
    
    
    # Кнопки навигации
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("register"), key="register_btn", use_container_width=True):
            st.session_state["auth_mode"] = "register"
            st.session_state["current_page"] = "auth"
            st.rerun()
    
    with col2:
        if st.button(t("login"), key="login_btn", use_container_width=True):
            st.session_state["auth_mode"] = "login"
            st.session_state["current_page"] = "auth"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Заголовок перед карточками
    st.markdown(f"""
    <style>
    .subtitle {{
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: #2d303a;  /* новый цвет */
        margin-bottom: 20px;
    }}
    </style>
    <h3 class="subtitle">{t("subtitle")}</h3>
    """, unsafe_allow_html=True)


     # --- Стили карточек ---
    st.markdown(
        """
        <style>
        .card {
            background-color: white;
            border: 2px solid #968cd2;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
            min-height: 160px; /* одинаковая высота карточек */
            margin-top: 20px;
        }
        .card-title {
            font-size: 20px;
            font-weight: 700;
            color: #2c2c2c;
            margin-bottom: 10px;
        }
        .card-desc {
            font-size: 15px;
            font-weight: 400;
            color: #444;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Карточки под кнопками ---
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(f"""
            <div class="card">
                <div class="card-title">{t("card_support_title")}</div>
                <div class="card-desc">{t("card_support_desc")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f"""
            <div class="card">
                <div class="card-title">{t("card_selfcare_title")}</div>
                <div class="card-desc">{t("card_selfcare_desc")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(f"""
            <div class="card">
                <div class="card-title">{t("card_analysis_title")}</div>
                <div class="card-desc">{t("card_analysis_desc")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f"""
            <div class="card">
                <div class="card-title">{t("card_multilang_title")}</div>
                <div class="card-desc">{t("card_multilang_desc")}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    # --- Нижняя центральная карточка: Личный кабинет ---
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-top: 20px; margin-bottom: 60px;">
            <div class="card" style="max-width: 400px; width: 100%;">
                <div class="card-title">{t("card_account_title")}</div>
                <div class="card-desc">{t("card_account_desc")}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <style>
    .subtitle {{
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: #2d303a;  /* новый цвет */
        margin-bottom: 20px;
    }}
    </style>
    <h3 class="subtitle">{t("try_now_title")}</h3>
    """, unsafe_allow_html=True)

    # Поле для текста (просто для вида, не сохраняем)
    user_text = st.text_area("", placeholder=t("textarea_placeholder"))

    # Кнопка → сразу на auth
    if st.button(t("analyze")):
        st.session_state["current_page"] = "auth"
        st.session_state["auth_mode"] = "register"  # или "login"
        st.rerun()
    
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