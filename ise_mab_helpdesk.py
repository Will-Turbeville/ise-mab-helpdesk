import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import re
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="HGTC ISE MAB Helpdesk App", layout="wide")
st.title("🛠️ HGTC ISE MAB Endpoint Manager")
st.caption("A Network Services Application")

# Session state for connection
if "ise_config" not in st.session_state:
    st.session_state.ise_config = {
        "url": os.getenv("ISE_URL", "https://ise-lab.hgtc.edu"),
        "user": os.getenv("ERS_USER", "ers_helpdesk"),
        "pass": os.getenv("ERS_PASS", ""),
        "verify": True
    }

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("ISE Connection Settings")
    url = st.text_input("ISE PAN URL", value=st.session_state.ise_config["url"])
    user = st.text_input("ERS Username", value=st.session_state.ise_config["user"])
    password = st.text_input("ERS Password", type="password", value=st.session_state.ise_config["pass"])
    verify = st.checkbox("Verify SSL Certificate", value=st.session_state.ise_config["verify"])
    
    if st.button("✅ Apply Connection", type="primary"):
        st.session_state.ise_config = {"url": url, "user": user, "pass": password, "verify": verify}
        with open(".env", "w") as f:
            f.write(f"ISE_URL={url}\nERS_USER={user}\nERS_PASS={password}\n")
        st.success("✅ .env file updated!")
        st.rerun()

ise_url = st.session_state.ise_config["url"]
ers_user = st.session_state.ise_config["user"]
ers_pass = st.session_state.ise_config["pass"]
verify_ssl = st.session_state.ise_config["verify"]

if not ers_pass:
    st.warning("Please enter credentials and click Apply Connection.")
    st.stop()

auth = HTTPBasicAuth(ers_user, ers_pass)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "ERS-Media-Type": "identity.endpointgroup.1.0"
}

st.success("✅ Settings loaded")

# Helper function
def normalize_mac(mac: str) -> str:
    cleaned = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
    if len(cleaned) != 12:
        raise ValueError("MAC must be 12 hexadecimal characters")
    return ":".join(cleaned[i:i+2] for i in range(0, 12, 2))

# Main UI
target_group = st.text_input("Target Endpoint Identity Group", value="mab_lab_quarantine")

if st.button("🔄 Load Group & MACs", type="primary"):
    try:
        with st.spinner("Loading..."):
            # Get group ID
            r = requests.get(f"{ise_url}/ers/config/endpointgroup?size=100", 
                           auth=auth, headers=headers, verify=verify_ssl, timeout=15)
            r.raise_for_status()
            groups = r.json().get("SearchResult", {}).get("resources", [])
            
            group_match = next((g for g in groups if g["name"].lower() == target_group.lower()), None)
            if not group_match:
                st.error("Group not found")
                st.stop()
            
            group_id = group_match["id"]
            st.session_state.group_id = group_id
            st.success(f"✅ Group: {group_match['name']} (ID: {group_id})")

            # Load MACs
            r2 = requests.get(f"{ise_url}/ers/config/endpoint?filter=groupId.EQ.{group_id}&size=100",
                            auth=auth, headers={"Accept": "application/json"}, verify=verify_ssl, timeout=15)
            r2.raise_for_status()
            
            resources = r2.json().get("SearchResult", {}).get("resources", [])
            mac_list = []
            for res in resources:
                detail = requests.get(res["link"]["href"], auth=auth, headers={"Accept": "application/json"}, verify=verify_ssl, timeout=10).json()
                ep = detail.get("ERSEndPoint", {})
                mac_list.append({"MAC": ep.get("mac"), "Description": ep.get("description", ""), "ID": ep.get("id")})
            
            st.success(f"Found {len(mac_list)} MAC(s)")
            if mac_list:
                st.dataframe(mac_list, use_container_width=True)
    except Exception as e:
        st.error(f"Load Error: {str(e)}")

# ================== ADD / UPDATE ==================
st.subheader("➕ Add or Update MAC")
col1, col2 = st.columns([2, 3])
with col1:
    new_mac = st.text_input("MAC Address", placeholder="00:11:22:33:44:55", key="add_mac")
with col2:
    new_desc = st.text_input("Description", placeholder="John's Laptop", key="add_desc")

if st.button("Add / Update MAC", type="primary"):
    if new_mac and "group_id" in st.session_state:
        try:
            mac_norm = normalize_mac(new_mac)
            
            payload = {
                "ERSEndPoint": {
                    "mac": mac_norm,
                    "groupId": st.session_state.group_id,
                    "staticGroupAssignment": True,
                    "description": new_desc or "Added via HGTC Helpdesk App"
                }
            }

            add_headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "ERS-Media-Type": "identity.endpoint.1.2"   # Important for endpoint
            }

            check = requests.get(
                f"{ise_url}/ers/config/endpoint?filter=mac.EQ.{mac_norm}",
                auth=auth, headers={"Accept": "application/json"}, verify=verify_ssl, timeout=10
            )
            existing = check.json().get("SearchResult", {}).get("resources", [])

            if existing:
                ep_id = existing[0]["id"]
                r = requests.put(f"{ise_url}/ers/config/endpoint/{ep_id}", 
                               json=payload, auth=auth, headers=add_headers, verify=verify_ssl, timeout=10)
            else:
                r = requests.post(f"{ise_url}/ers/config/endpoint", 
                                json=payload, auth=auth, headers=add_headers, verify=verify_ssl, timeout=10)

            r.raise_for_status()
            st.success(f"✅ MAC **{mac_norm}** added/updated successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Add Error: {str(e)}")
    else:
        st.warning("Load the group first.")

# ================== REMOVE ==================
st.subheader("🗑️ Remove MAC")
remove_mac = st.text_input("MAC to Remove", placeholder="00:11:22:33:44:55", key="remove_mac")

if st.button("Remove MAC", type="secondary"):
    if remove_mac and "group_id" in st.session_state:
        try:
            mac_norm = normalize_mac(remove_mac)
            
            # Find endpoint
            check = requests.get(
                f"{ise_url}/ers/config/endpoint?filter=mac.EQ.{mac_norm}",
                auth=auth, headers={"Accept": "application/json"}, verify=verify_ssl, timeout=10
            )
            resources = check.json().get("SearchResult", {}).get("resources", [])
            
            if not resources:
                st.warning("MAC not found")
                st.stop()
            
            ep_id = resources[0]["id"]
            
            # Remove static assignment
            payload = {
                "ERSEndPoint": {
                    "staticGroupAssignment": False
                }
            }
            
            remove_headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "ERS-Media-Type": "identity.endpoint.1.2"   # Critical for endpoint PUT
            }
            
            r = requests.put(
                f"{ise_url}/ers/config/endpoint/{ep_id}", 
                json=payload, 
                auth=auth, 
                headers=remove_headers, 
                verify=verify_ssl, 
                timeout=10
            )
            r.raise_for_status()
            st.success(f"✅ MAC **{mac_norm}** removed from static group!")
            st.rerun()
        except Exception as e:
            st.error(f"Remove Error: {str(e)}")
    else:
        st.warning("Load the group first.")