import streamlit as st

st.set_page_config(page_title="AI Эмо-дневник", layout="centered")

# Стили кнопок
st.markdown("""
    <style>
    .button-container {
        display: flex;
        justify-content: flex-start;
        gap: 10px;
        margin-bottom: 30px;
    }
    .custom-button {
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        cursor: pointer;
    }
    .green-btn {
        background-color: #4CAF50;
    }
    .blue-btn {
        background-color: #2196F3;
    }
    </style>
""", unsafe_allow_html=True)

# Кнопки — делаем через колонку, чтобы стилизовать и ловить клики
col1, col2 = st.columns(2)
with col1:
    if st.button("Зарегистрироваться", key="register_btn"):
        st.session_state["auth_mode"] = "register"
        st.switch_page("auth_page")
with col2:
    if st.button("Войти", key="login_btn"):
        st.session_state["auth_mode"] = "login"
        st.switch_page("auth_page")

# Заголовок
st.markdown("<h1 style='text-align: center;'>AI Эмо-дневник</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Добро пожаловать! Это приложение поможет вам отслеживать ваше настроение и получать поддержку.</p>", unsafe_allow_html=True)
