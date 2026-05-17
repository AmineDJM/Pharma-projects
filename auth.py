import bcrypt
import streamlit as st
from db import get_session, User, UserPermission, ProductionLine
from config import CATEGORIES

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

def create_default_admin():
    db = get_session()
    try:
        existing = db.query(User).filter_by(username="admin").first()
        if not existing:
            user = User(username="admin", password_hash=hash_password("admin123"), role="admin", is_active=True)
            db.add(user)
            db.commit()
    finally:
        db.close()

def authenticate(username, password):
    db = get_session()
    try:
        user = db.query(User).filter_by(username=username, is_active=True).first()
        if user and check_password(password, user.password_hash):
            return {"id": user.id, "username": user.username, "role": user.role}
        return None
    finally:
        db.close()

def login_widget():
    st.title("AT Pharma — Project Tracker")
    st.caption("Connexion locale")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Se connecter", type="primary"):
        user = authenticate(username, password)
        if user:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Identifiants incorrects.")

def current_user():
    return st.session_state.get("user")

def logout_button():
    if st.sidebar.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

def is_admin():
    u = current_user()
    return bool(u and u["role"] == "admin")

def user_permissions(user_id):
    db = get_session()
    try:
        perms = db.query(UserPermission).filter_by(user_id=user_id).all()
        return [
            {
                "production_line": p.production_line,
                "category": p.category,
                "can_view": p.can_view,
                "can_edit": p.can_edit,
            }
            for p in perms
        ]
    finally:
        db.close()

def can_view_line_category(user, line, category):
    if user["role"] == "admin":
        return True
    perms = user_permissions(user["id"])
    return any(p["production_line"] == line and p["category"] == category and p["can_view"] for p in perms)

def can_edit_line_category(user, line, category):
    if user["role"] == "admin":
        return True
    if user["role"] == "viewer":
        return False
    perms = user_permissions(user["id"])
    return any(p["production_line"] == line and p["category"] == category and p["can_edit"] for p in perms)

def accessible_lines(user):
    db = get_session()
    try:
        all_lines = [x.name for x in db.query(ProductionLine).all()]
    finally:
        db.close()
    if user["role"] == "admin":
        return all_lines
    perms = user_permissions(user["id"])
    return sorted(set(p["production_line"] for p in perms if p["can_view"]))

def accessible_categories(user, line):
    if user["role"] == "admin":
        return list(CATEGORIES.keys())
    return [cat for cat in CATEGORIES.keys() if can_view_line_category(user, line, cat)]
