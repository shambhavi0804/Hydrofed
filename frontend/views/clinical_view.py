"""
Clinical Inputs Summary View for HydroFed-ICAF.
"""

import streamlit as st
from frontend.components import render_header, render_patient_banner, render_metric_card, render_disclaimer

def render_clinical_view():
    render_header(
        "Clinical Demographics & Physiological Input Summary",
        "Parameters incorporated into the Adaptive Immune Cross-Attention (AICA) embedding matrix."
    )

    active_id = st.session_state.get("active_patient_id")
    if not active_id:
        st.markdown("""
        <div class="clinical-banner clinical-banner-warning">
            ⚠️ <b>No Active Patient Loaded</b> — Please look up or register a patient profile.
        </div>
        """, unsafe_allow_html=True)
        render_disclaimer()
        return

    data = st.session_state.get("active_patient_data") or {}
    render_patient_banner(active_id, data)

    st.subheader("Active Physiological Demographic Variables")
    c1, c2, c3, c4, c5 = st.columns(5)
    render_metric_card("Patient Age", f"{data.get('age', 5.0)} Years", card_type="default", col=c1)
    render_metric_card("Biological Gender", str(data.get('gender', 'Male')), card_type="default", col=c2)
    render_metric_card("Diabetes Mellitus", "Present" if data.get('diabetes') == 1 else "Absent", card_type="default", col=c3)
    render_metric_card("Passive Smoke", "Exposed" if data.get('passive_smoke_exposure') == 1 else "None", card_type="default", col=c4)
    render_metric_card("Family Respiratory", "Positive" if data.get('family_respiratory_history') == 1 else "Negative", card_type="default", col=c5)

    st.subheader("Supplemental Hospital Clinical Parameters")
    c_bp, c_fbs, c_hw = st.columns(3)
    render_metric_card("Blood Pressure", str(data.get('blood_pressure', '105/70 mmHg')), card_type="default", col=c_bp)
    render_metric_card("Fasting Blood Sugar", str(data.get('fasting_blood_sugar', '88 mg/dL')), card_type="default", col=c_fbs)
    render_metric_card("Physical Stature", f"{data.get('height', '110 cm')} / {data.get('weight', '19.5 kg')}", card_type="default", col=c_hw)

    st.markdown("""
    <div class="clinical-banner clinical-banner-info">
        ℹ️ <b>Neural Encoding:</b> These variables are projected through a 5-dimensional linear embedding layer 
        before interacting with the visual feature maps via bidirectional cross-attention mechanisms.
    </div>
    """, unsafe_allow_html=True)

    render_disclaimer()
