import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import re
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ISE MAB Helpdesk App", layout="wide")

# ===================== AUTHENTICATION =====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None   # "admin" or "user"
    st.session_state.username = None

# Login Page
if not st.session_state.logged_in:
    st.title("🔐 ISE MAB Helpdesk Login")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Sign In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.session_state.username = username
                st.rerun()
            elif username == "user" and password == "user123":
                st.session_state.logged_in = True
                st.session_state.user_role = "user"
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()  # Stop execution until logged in

# ===================== MAIN APPLICATION =====================
st.title("🛠️ ISE MAB Endpoint Manager")
st.caption("Helpdesk Tool for Cisco ISE")

# Sidebar Info
st.sidebar.success(f"Logged in as: **{st.session_state.username}** ({st.session_state.user_role})")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# Show Settings page only for Admins
if st.session_state.user_role == "admin":
    st.sidebar.page_link("pages/1_Settings.py", label="⚙️ Settings")

# ===================== SESSION STATE =====================
if "ise_config" not in st.session_state:
    st.session_state.ise_config = {
        "url": os.getenv("ISE_URL", "https://ise.example.com"),
        "user": os.getenv("ERS_USER", "ers_helpdesk"),
        "pass": os.getenv("ERS_PASS", ""),
        "verify": False
    }

if "group_id" not in st.session_state:
    st.session_state.group_id = None

# ===================== HELPER FUNCTION =====================
def normalize_mac(mac: str) -> str:
    cleaned = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
    if len(cleaned) != 12:
        raise ValueError("MAC must be 12 hexadecimal characters")
    return ":".join(cleaned[i:i+2] for i in range(0, 12, 2))

# ===================== MAIN UI =====================
st.success("✅ Application Ready")

target_group = st.text_input("Target Endpoint Identity Group", value="MAB-Devices")

if st.button("🔄 Load Group & MACs", type="primary"):
    try:
        with st.spinner("Loading..."):
            auth = HTTPBasicAuth(st.session_state.ise_config["user"], st.session_state.ise_config["pass"])

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "ERS-Media-Type": "identity.endpointgroup.1.0"
            }

            r = requests.get(f"{st.session_state.ise_config['url']}/ers/config/endpointgroup?size=100",
                           auth=auth, headers=headers, verify=st.session_state.ise_config["verify"], timeout=15)
            r.raise_for_status()
            
            groups = r.json().get("SearchResult", {}).get("resources", [])
            group_match = next((g for g in groups if g["name"].lower() == target_group.lower()), None)
            
            if not group_match:
                st.error("Group not found")
                st.stop()
            
            st.session_state.group_id = group_match["id"]
            st.success(f"✅ Group loaded: {group_match['name']}")

            r2 = requests.get(f"{st.session_state.ise_config['url']}/ers/config/endpoint?filter=groupId.EQ.{st.session_state.group_id}&size=100",
                            auth=auth, headers={"Accept": "application/json"}, verify=st.session_state.ise_config["verify"], timeout=15)
            r2.raise_for_status()
            
            resources = r2.json().get("SearchResult", {}).get("resources", [])
            mac_list = []
            for res in resources:
                detail = requests.get(res["link"]["href"], auth=auth, headers={"Accept": "application/json"}, 
                                    verify=st.session_state.ise_config["verify"], timeout=10).json()
                ep = detail.get("ERSEndPoint", {})
                mac_list.append({
                    "MAC": ep.get("mac"),
                    "Description": ep.get("description", ""),
                    "ID": ep.get("id")
                })
            
            st.success(f"Found {len(mac_list)} MAC(s)")
            if mac_list:
                st.dataframe(mac_list, use_container_width=True)
    except Exception as e:
        st.error(f"Load Error: {str(e)}")

# ===================== ADD / UPDATE MAC =====================
st.subheader("➕ Add or Update MAC")
col1, col2 = st.columns([2, 3])
with col1:
    new_mac = st.text_input("MAC Address", placeholder="00:11:22:33:44:55", key="add_mac")
with col2:
    new_desc = st.text_input("Description", placeholder="John's Laptop", key="add_desc")

if st.button("Add / Update MAC", type="primary"):
    if new_mac and st.session_state.group_id:
        try:
            mac_norm = normalize_mac(new_mac)
            auth = HTTPBasicAuth(st.session_state.ise_config["user"], st.session_state.ise_config["pass"])
            
            payload = {
                "ERSEndPoint": {
                    "mac": mac_norm,
                    "groupId": st.session_state.group_id,
                    "staticGroupAssignment": True,
                    "description": new_desc or "Added via Helpdesk App"
                }
            }

            headers = {"Accept": "application/json", "Content-Type": "application/json", "ERS-Media-Type": "identity.endpoint.1.2"}

            check = requests.get(f"{st.session_state.ise_config['url']}/ers/config/endpoint?filter=mac.EQ.{mac_norm}",
                               auth=auth, headers={"Accept": "application/json"}, verify=st.session_state.ise_config["verify"], timeout=10)
            existing = check.json().get("SearchResult", {}).get("resources", [])

            if existing:
                r = requests.put(f"{st.session_state.ise_config['url']}/ers/config/endpoint/{existing[0]['id']}", 
                               json=payload, auth=auth, headers=headers, verify=st.session_state.ise_config["verify"], timeout=10)
            else:
                r = requests.post(f"{st.session_state.ise_config['url']}/ers/config/endpoint", 
                                json=payload, auth=auth, headers=headers, verify=st.session_state.ise_config["verify"], timeout=10)

            r.raise_for_status()
            st.success(f"✅ MAC {mac_norm} added/updated!")
            st.rerun()
        except Exception as e:
            st.error(f"Add Error: {str(e)}")
    else:
        st.warning("Please load a group first")

# ===================== REMOVE MAC =====================
st.subheader("🗑️ Remove MAC")
remove_mac = st.text_input("MAC to Remove", placeholder="00:11:22:33:44:55", key="remove_mac")

if st.button("Remove MAC", type="secondary"):
    if remove_mac and st.session_state.group_id:
        try:
            mac_norm = normalize_mac(remove_mac)
            auth = HTTPBasicAuth(st.session_state.ise_config["user"], st.session_state.ise_config["pass"])
            
            check = requests.get(f"{st.session_state.ise_config['url']}/ers/config/endpoint?filter=mac.EQ.{mac_norm}",
                               auth=auth, headers={"Accept": "application/json"}, verify=st.session_state.ise_config["verify"], timeout=10)
            resources = check.json().get("SearchResult", {}).get("resources", [])
            
            if not resources:
                st.warning("MAC not found")
            else:
                ep_id = resources[0]["id"]
                payload = {"ERSEndPoint": {"staticGroupAssignment": False}}
                headers = {"Accept": "application/json", "Content-Type": "application/json", "ERS-Media-Type": "identity.endpoint.1.2"}
                
                r = requests.put(f"{st.session_state.ise_config['url']}/ers/config/endpoint/{ep_id}", 
                               json=payload, auth=auth, headers=headers, verify=st.session_state.ise_config["verify"], timeout=10)
                r.raise_for_status()
                st.success(f"✅ MAC {mac_norm} removed!")
                st.rerun()
        except Exception as e:
            st.error(f"Remove Error: {str(e)}")
    else:
        st.warning("Please load a group first")