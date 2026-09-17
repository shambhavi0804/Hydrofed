"""
Clinical Navigation and Sidebar Component for HydroFed-ICAF.
"""

import streamlit as st

def render_sidebar():
    """Renders the institutional sidebar, branding, user session, and navigation menu."""
    
    # 1. Institutional Branding
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 10px 0 15px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 15px;">
        <div style="font-size: 1.35rem; font-weight: 800; color: #173B65; letter-spacing: -0.02em;">HYDROFED-ICAF</div>
        <div style="font-size: 0.72rem; font-weight: 700; color: #2563EB; letter-spacing: 0.1em; text-transform: uppercase;">Decentralized Clinical CDSS</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Signed In User Metadata
    user_name = st.session_state.get("user_name", "Clinician")
    user_role = st.session_state.get("user_role", "Clinician").title()
    
    st.sidebar.markdown(f"""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 12px; margin-bottom: 15px; font-size: 0.82rem;">
        <div><b>User:</b> {user_name}</div>
        <div><b>Role:</b> <span class="badge badge-primary" style="padding: 2px 6px; font-size: 0.7rem;">{user_role}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Clinical Navigation Structure
    navigation_sections = {
        "Clinical Diagnostic Workflow": [
            "🏠 Dashboard",
            "📝 Patient Registration / Search",
            "🩻 X-ray Analysis",
            "📋 Clinical Inputs",
            "🧬 CDSS Results",
            "🔍 Explainability",
            "📈 Longitudinal View",
            "📄 Clinical Report"
        ],
        "Decentralized Infrastructure": [
            "⚡ Edge Performance",
            "🌐 Network",
            "💧 Flow",
            "🛡️ Security"
        ],
        "System Science & Audit": [
            "📊 Experiments",
            "⚖️ Analytics",
            "📐 Model Information",
            "📑 Audit"
        ]
    }

    if st.session_state.get("user_role") == "admin":
        navigation_sections["System Science & Audit"].append("👤 Admin Management")

    all_pages = []
    for section_items in navigation_sections.values():
        all_pages.extend(section_items)

    selected_page = st.sidebar.radio(
        "Navigation",
        all_pages,
        label_visibility="collapsed"
    )

    # 4. Active Patient Summary Widget at bottom of sidebar
    st.sidebar.markdown("<hr style='margin: 15px 0 10px 0; border-color: #E2E8F0;'/>", unsafe_allow_html=True)
    active_pat = st.session_state.get("active_patient_id", "")
    if active_pat:
        st.sidebar.markdown(f"""
        <div class="metric-card metric-card-primary" style="padding: 10px; margin-bottom: 10px;">
            <span class="card-label" style="font-size: 0.7rem;">Active Patient</span>
            <div style="font-size: 1rem; font-weight: 700; color: #173B65;">{active_pat}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div class="metric-card" style="padding: 10px; text-align: center; margin-bottom: 10px; background: #FFFBEB !important; border-color: #FDE68A !important;">
            <span style="font-size: 0.75rem; color: #B45309; font-weight: 700;">NO PATIENT LOADED</span>
        </div>
        """, unsafe_allow_html=True)

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_name = ""
        st.session_state.user_role = ""
        st.session_state.active_patient_id = ""
        st.session_state.active_patient_data = None
        st.session_state.diagnostic_results = None
        st.rerun()

    return selected_page
