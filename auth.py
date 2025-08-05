import streamlit as st
from supabase import create_client
import hashlib

# --- Инициализация Supabase ---
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# --- Хэширование пароля ---
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# --- Регистрация ---
def signup_user(username: str, email: str, password: str) -> bool:
    hashed_pw = hash_password(password)

    # Проверка, существует ли email уже
    existing_user = supabase.table("users").select("*").eq("email", email).execute()
    if existing_user.data and len(existing_user.data) > 0:
        st.error("Пользователь с таким email уже существует.")
        return False

    # Добавляем пользователя
    response = supabase.table("users").insert({
        "username": username,
        "email": email,
        "password": hashed_pw
    }).execute()

    # Проверяем успешность добавления
    if hasattr(response, "status_code") and response.status_code == 201:
        st.success("Регистрация прошла успешно!")
        return True
    else:
        st.error("Ошибка при регистрации.")
        return False

# --- Вход ---
def login_user(email: str, password: str) -> bool:
    hashed_pw = hash_password(password)

    response = supabase.table("users").select("*").eq("email", email).eq("password", hashed_pw).execute()

    if response.data and len(response.data) > 0:
        user = response.data[0]
        st.session_state["user"] = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
        st.success(f"Добро пожаловать, {user['username']}!")
        return True
    else:
        st.error("Неверный email или пароль.")
        return False

# --- Получение текущего пользователя ---
def get_current_user():
    return st.session_state.get("user")
