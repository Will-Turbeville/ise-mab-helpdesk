import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.title("⚙️ Settings")
st.header("ISE Connection Configuration")

# Use session state
if "ise_config" not in st.session_state:
    st.session_state.ise_config = {
        "url": os.getenv("ISE_URL", "https://ise.example.com"),
        "user": os.getenv("ERS_USER", "ers_helpdesk"),
        "pass": os.getenv("ERS_PASS", ""),
        "verify": False,
        "auth_type": "Basic Auth"
    }

col1, col2 = st.columns(2)
with col1:
    url = st.text_input("ISE PAN URL", value=st.session_state.ise_config["url"])
    user = st.text_input("ERS Username", value=st.session_state.ise_config["user"])
with col2:
    password = st.text_input("ERS Password", type="password", value=st.session_state.ise_config["pass"])
    verify = st.checkbox("Verify SSL Certificate", value=st.session_state.ise_config["verify"])

auth_type = st.selectbox("Authentication Type", ["Basic Auth", "SSO (Coming Soon)"])

if st.button("💾 Save Settings", type="primary"):
    st.session_state.ise_config = {
        "url": url,
        "user": user,
        "pass": password,
        "verify": verify,
        "auth_type": auth_type
    }
    
    with open(".env", "w") as f:
        f.write(f"ISE_URL={url}\n")
        f.write(f"ERS_USER={user}\n")
        f.write(f"ERS_PASS={password}\n")
    
    st.success("✅ Settings saved successfully!")
    st.rerun()

st.info("Changes will be used immediately after saving.")