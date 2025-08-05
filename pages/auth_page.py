import streamlit as st

st.set_page_config(page_title="Авторизация", layout="centered", initial_sidebar_state="collapsed")

# Определяем режим
mode = st.session_state.get("auth_mode", "login")

# Назад
if st.button("← Назад на главную"):
    st.switch_page("main")

# Заголовки
st.markdown("<h1 style='text-align: center;'>AI Эмо-дневник</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Пожалуйста, войдите или зарегистрируйтесь, чтобы продолжить.</p>", unsafe_allow_html=True)

# Кастомные стили
st.markdown("""
    <style>
    .switch-button {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
    .green-btn { background-color: #4CAF50; }
    .blue-btn { background-color: #2196F3; }
    </style>
""", unsafe_allow_html=True)

# Переключение режима
col1, col2 = st.columns(2)
with col1:
    if st.button("Регистрация", key="switch_to_register"):
        st.session_state["auth_mode"] = "register"
        st.rerun()
with col2:
    if st.button("Войти", key="switch_to_login"):
        st.session_state["auth_mode"] = "login"
        st.rerun()

# Форма авторизации
with st.form("auth_form"):
    st.text_input("Email")
    if mode == "register":
        st.text_input("Имя пользователя")
    st.text_input("Пароль", type="password")
    submitted = st.form_submit_button("Зарегистрироваться" if mode == "register" else "Войти")

    if submitted:
        st.success("Успешно!")
        st.switch_page("diary")

# Ссылки-подписи снизу
if mode == "register":
    if st.button("Уже есть аккаунт? Войти", key="to_login"):
        st.session_state["auth_mode"] = "login"
        st.rerun()
else:
    if st.button("Нет аккаунта? Зарегистрироваться", key="to_register"):
        st.session_state["auth_mode"] = "register"
        st.rerun()
