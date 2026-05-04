import streamlit as st
import os
import json
from dotenv import load_dotenv

load_dotenv()

# ===================== SECURITY CHECK =====================
if ("logged_in" not in st.session_state or 
    not st.session_state.logged_in or 
    st.session_state.user_role != "admin"):
    st.error("⛔ Access Denied: Admin privileges required")
    st.stop()

# ===================== SETTINGS PAGE =====================
st.title("⚙️ Settings")
st.header("ISE Connection Configuration")

# --- ISE Connection Section ---
if "ise_config" not in st.session_state:
    st.session_state.ise_config = {
        "url": os.getenv("ISE_URL", "https://ise.example.com"),
        "user": os.getenv("ERS_USER", "ers_helpdesk"),
        "pass": os.getenv("ERS_PASS", ""),
        "verify": False
    }

col1, col2 = st.columns(2)
with col1:
    url = st.text_input("ISE PAN URL", value=st.session_state.ise_config["url"])
    user = st.text_input("ERS Username", value=st.session_state.ise_config["user"])
with col2:
    password = st.text_input("ERS Password", type="password", value=st.session_state.ise_config["pass"])
    verify = st.checkbox("Verify SSL Certificate", value=st.session_state.ise_config["verify"])

if st.button("💾 Save ISE Settings", type="primary"):
    st.session_state.ise_config = {
        "url": url, "user": user, "pass": password, "verify": verify
    }
    with open(".env", "w") as f:
        f.write(f"ISE_URL={url}\nERS_USER={user}\nERS_PASS={password}\n")
    st.success("✅ ISE Settings Saved!")

st.divider()

# ===================== LOGIN ACCOUNTS MANAGEMENT =====================
st.header("🔑 Manage Login Accounts")

# Load or initialize credentials
if "credentials" not in st.session_state:
    st.session_state.credentials = {
        "admin": {"username": "admin", "password": "admin123"},
        "user": {"username": "user", "password": "user123"}
    }

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Admin Account")
    admin_user = st.text_input("Admin Username", value=st.session_state.credentials["admin"]["username"], key="admin_user")
    admin_pass = st.text_input("Admin Password", value=st.session_state.credentials["admin"]["password"], type="password", key="admin_pass")

with col_b:
    st.subheader("User Account")
    user_user = st.text_input("User Username", value=st.session_state.credentials["user"]["username"], key="user_user")
    user_pass = st.text_input("User Password", value=st.session_state.credentials["user"]["password"], type="password", key="user_pass")

if st.button("💾 Save Login Accounts", type="primary"):
    st.session_state.credentials = {
        "admin": {"username": admin_user, "password": admin_pass},
        "user": {"username": user_user, "password": user_pass}
    }
    st.success("✅ Login accounts updated successfully!")
    st.info("Note: You will need to log out and log back in for changes to take effect.")

st.caption("Default: admin / admin123    |    user / user123")