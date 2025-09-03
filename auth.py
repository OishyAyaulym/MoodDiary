import streamlit as st
from supabase import create_client
import hashlib
from lang import t
from db import create_user, get_user_by_email, get_user_by_username

# --- Инициализация Supabase ---
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]  # anon key для Auth
    return create_client(url, key)

# --- Инициализация Supabase с Service Role Key (для таблицы users) ---
@st.cache_resource
def get_supabase_service():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
supabase_service = get_supabase_service()

# --- Хэширование пароля (для своей таблицы users) ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# --- Регистрация ---
def signup_user(username: str, email: str, password: str) -> bool:
    if get_user_by_email(email):
        st.error(t("email_exists"))
        return False
    if get_user_by_username(username):
        st.error(t("username_exists"))
        return False

    try:
        # Создаём пользователя в Supabase Auth
        auth_response = supabase.auth.sign_up({"email": email, "password": password})
        if not auth_response.user:
            st.error(t("register_error"))
            return False

        # Сохраняем в таблицу users через Service Role (чтобы не было RLS ошибок)
        create_user(username=username, email=email, user_id=auth_response.user.id)

        st.success(t("success_register"))
        return True
    except Exception as e:
        st.error(f"{t('register_error')} {e}")
        return False
    
# --- Вход ---
def login_user(email: str, password: str) -> bool:
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if not auth_response.user:
            st.error(t("username_email_error"))
            return False

        user_data = get_user_by_email(email)
        if not user_data:
            st.error(t("user_not_found"))
            return False

        st.session_state["user"] = {
            "id": auth_response.user.id,
            "email": auth_response.user.email,
            "username": user_data["username"]
        }
        st.success(f"{t('welcome')} {user_data['username']}!")
        return True

    except Exception as e:
        st.error(f"{t('username_email_error')} {e}")
        return False

# --- Получение текущего пользователя ---
def get_current_user():
    return st.session_state.get("user")