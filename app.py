"""
HydroFed-ICAF: Bio-Inspired Decentralized Clinical Decision Support System.
Main Streamlit Application Entry Point.
"""

import os
import sys
import hashlib
import hmac
import secrets
from datetime import datetime
import streamlit as st

# Add workspace root to Python path
sys.path.append(os.getcwd())

from database.schema import init_database, get_db_connection
from cdss.inference_service import InferenceService
from frontend.styles import inject_clinical_css
from frontend.navigation import render_sidebar

# Import Views
from frontend.views.dashboard_view import render_dashboard_view
from frontend.views.patient_view import render_patient_view
from frontend.views.xray_view import render_xray_view
from frontend.views.clinical_view import render_clinical_view
from frontend.views.cdss_view import render_cdss_view
from frontend.views.xai_view import render_xai_view
from frontend.views.longitudinal_view import render_longitudinal_view
from frontend.views.report_view import render_report_view
from frontend.views.edge_view import render_edge_view
from frontend.views.network_view import render_network_view
from frontend.views.flow_view import render_flow_view
from frontend.views.security_view import render_security_view
from frontend.views.experiments_view import render_experiments_view
from frontend.views.analytics_view import render_analytics_view
from frontend.views.model_view import render_model_view
from frontend.views.audit_view import render_audit_view
from frontend.views.admin_view import render_admin_view

# ==============================================================================
# 1. APPLICATION INITIALIZATION & CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="HydroFed-ICAF Clinic Portal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema
init_database()

# Inject modern clinical CSS
inject_clinical_css()

# Cache heavy backend services
@st.cache_resource
def get_inference_service():
    return InferenceService()

@st.cache_resource
def get_experiment_runner():
    from experiments.run_experiment import UnifiedExperimentRunner
    return UnifiedExperimentRunner()

# ==============================================================================
# 2. SESSION STATE MANAGEMENT
# ==============================================================================
if 'active_patient_id' not in st.session_state:
    st.session_state.active_patient_id = ""
if 'active_patient_data' not in st.session_state:
    st.session_state.active_patient_data = None
if 'diagnostic_results' not in st.session_state:
    st.session_state.diagnostic_results = None
if 'fl_round' not in st.session_state:
    st.session_state.fl_round = 0
if 'fl_consensus_history' not in st.session_state:
    st.session_state.fl_consensus_history = []
if 'fl_flow_levels' not in st.session_state:
    st.session_state.fl_flow_levels = [0.75, 0.40, 0.60]
if 'fl_sec_encrypted_count' not in st.session_state:
    st.session_state.fl_sec_encrypted_count = 0

# ==============================================================================
# 3. HOSPITAL AUTHENTICATION LAYER
# ==============================================================================
def _hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"pbkdf2_sha256$200000${salt.hex()}${digest.hex()}"

def _verify_password(password, stored):
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)).hex()
        return hmac.compare_digest(candidate, digest_hex)
    except Exception:
        return False

def init_auth_table():
    conn = get_db_connection()
    conn.execute("""CREATE TABLE IF NOT EXISTS app_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'clinician',
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

def user_count():
    conn = get_db_connection()
    n = conn.execute("SELECT COUNT(*) FROM app_users").fetchone()[0]
    conn.close()
    return n

def create_user(username, password, role="admin"):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO app_users(username, password_hash, role, active, created_at) VALUES (?, ?, ?, ?, ?)",
            (username.strip(), _hash_password(password), role, 1, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
        return True, "User created successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def authenticate(username, password):
    conn = get_db_connection()
    row = conn.execute("SELECT username, password_hash, role FROM app_users WHERE username=? AND active=1", (username.strip(),)).fetchone()
    conn.close()
    if row and _verify_password(password, row[1]):
        return {"username": row[0], "role": row[2]}
    return None

init_auth_table()
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# Authentication Gateway
if not st.session_state.authenticated:
    st.markdown("""
    <div style='max-width: 580px; margin: 40px auto 20px auto; text-align: center;'>
        <h1 style='color: #173B65 !important; border-bottom: none !important;'>HYDROFED-ICAF</h1>
        <div style='color: #2563EB; font-weight: 700; font-size: 0.95rem; letter-spacing: 0.08em; text-transform: uppercase;'>Decentralized Clinical Decision Support System</div>
        <p style='color: #64748B; font-size: 0.9rem; margin-top: 6px;'>Secure Hospital Practitioner Workspace</p>
    </div>
    """, unsafe_allow_html=True)

    c_center = st.columns([1, 2, 1])[1]
    with c_center:
        if user_count() == 0:
            st.info("Hospital System Setup: Create the initial administrator account.")
            with st.form("first_admin_setup"):
                username = st.text_input("Administrator Username")
                password = st.text_input("Administrator Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Administrator Account", type="primary", use_container_width=True)
                if submitted:
                    if not username.strip() or len(password) < 8:
                        st.error("Username is required and password must contain at least 8 characters.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    else:
                        ok, msg = create_user(username, password, "admin")
                        if ok:
                            st.success("Administrator account created. Please sign in.")
                            st.rerun()
                        else:
                            st.error(f"Unable to create administrator: {msg}")
        else:
            with st.form("hospital_login_form"):
                st.subheader("Hospital Practitioner Sign In")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In to Clinical Workspace", type="primary", use_container_width=True)
                if submitted:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_name = user["username"]
                        st.session_state.user_role = user["role"]
                        st.rerun()
                    else:
                        st.error("Invalid username or password credentials.")

        st.caption("Investigational Research Prototype — CDSS outputs support clinical assessment and do not replace qualified medical diagnosis.")
    st.stop()

# ==============================================================================
# 4. SIDEBAR NAVIGATION & ROUTING
# ==============================================================================
selected_page = render_sidebar()

# Route to active view
if selected_page == "🏠 Dashboard":
    render_dashboard_view()
elif selected_page == "📝 Patient Registration / Search":
    render_patient_view()
elif selected_page == "🩻 X-ray Analysis":
    render_xray_view(get_inference_service())
elif selected_page == "📋 Clinical Inputs":
    render_clinical_view()
elif selected_page == "🧬 CDSS Results":
    render_cdss_view()
elif selected_page == "🔍 Explainability":
    render_xai_view()
elif selected_page == "📈 Longitudinal View":
    render_longitudinal_view()
elif selected_page == "📄 Clinical Report":
    render_report_view()
elif selected_page == "⚡ Edge Performance":
    render_edge_view()
elif selected_page == "🌐 Network":
    render_network_view(get_experiment_runner)
elif selected_page == "💧 Flow":
    render_flow_view()
elif selected_page == "🛡️ Security":
    render_security_view()
elif selected_page == "📊 Experiments":
    render_experiments_view()
elif selected_page == "⚖️ Analytics":
    render_analytics_view()
elif selected_page == "📐 Model Information":
    render_model_view()
elif selected_page == "📑 Audit":
    render_audit_view()
elif selected_page == "👤 Admin Management":
    render_admin_view(create_user)
