"""
CDSS Results and Clinician Review Cockpit for HydroFed-ICAF.
"""

import os
import streamlit as st
from database.visit_repository import VisitRepository
from database.audit_repository import AuditRepository
from frontend.components import (
    render_header, render_patient_banner, render_metric_card,
    render_uncertainty_alert, render_disclaimer
)

def render_cdss_view():
    render_header(
        "CDSS Diagnostic Prediction Cockpit",
        "Multimodal classification scores, safety uncertainty boundaries, and clinician diagnostic signing."
    )

    res = st.session_state.get("diagnostic_results")
    if not res:
        st.markdown("""
        <div class="clinical-banner clinical-banner-warning">
            ⚠️ <b>No Active Diagnostic Evaluation</b> — Please navigate to <b>X-ray Analysis</b> and execute the diagnostics pipeline first.
        </div>
        """, unsafe_allow_html=True)
        render_disclaimer()
        return

    active_id = st.session_state.get("active_patient_id", "")
    render_patient_banner(active_id, st.session_state.get("active_patient_data"))

    visit_id = res.get('visit_id', 'N/A')

    # 1. Image Previews
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.subheader("Raw Input Chest Radiograph")
        raw_p = res.get('raw_image_path', '')
        if raw_p and os.path.exists(raw_p):
            st.image(raw_p, caption=f"Raw Image: {os.path.basename(raw_p)}", use_container_width=True)
        else:
            st.info("Raw image file not available.")

    with col_img2:
        st.subheader("Preprocessed Visual Representation")
        prep_p = res.get('preprocessed_image_path', '')
        if prep_p and os.path.exists(prep_p):
            st.image(prep_p, caption="CLAHE Normalized & Padded (224x224)", use_container_width=True)
        else:
            st.info("Preprocessed image not available.")

    # 2. Key Diagnostic Metrics
    st.subheader("Multimodal Diagnostic Indicators")
    pred_class = "PNEUMONIA" if res.get('predicted_class') == 1 else "NORMAL"
    pred_type = "danger" if res.get('predicted_class') == 1 else "success"
    prob_pneu = res.get('pneumonia_probability', 0.0)
    prob_norm = max(0.0, 1.0 - prob_pneu)
    confidence = res.get('confidence', 0.0)
    uncertainty = res.get('uncertainty', 0.0)
    latency = res.get('total_cdss_latency', 0.0)
    latency_ms = latency * 1000.0 if latency < 10.0 else latency

    m1, m2, m3, m4, m5 = st.columns(5)
    render_metric_card("Prediction", pred_class, card_type=pred_type, col=m1)
    render_metric_card("Pneumonia Prob.", f"{prob_pneu:.2%}", card_type="default", col=m2)
    render_metric_card("Normal Prob.", f"{prob_norm:.2%}", card_type="default", col=m3)
    render_metric_card("Confidence", f"{confidence:.2%}", card_type="default", col=m4)
    render_metric_card("Uncertainty (MC)", f"{uncertainty:.4f}", card_type="warning" if uncertainty > 0.15 else "default", col=m5)

    # 3. Uncertainty Safety Boundary Alert
    render_uncertainty_alert(uncertainty, threshold=0.15)

    # 4. Model Architecture & Pipeline Metadata
    st.subheader("Model Specifications & Execution Context")
    inf_c1, inf_c2, inf_c3 = st.columns(3)
    render_metric_card("Model Architecture", "DenseNet-151 + BMTF + IIFR + AICA", subtext="Dual-branch visual frequency & cross-attention", col=inf_c1)
    render_metric_card("Inference Engine", "PyTorch MC-Dropout", subtext="15 stochastic evaluation forward passes", col=inf_c2)
    render_metric_card("Total Pipeline Latency", f"{latency_ms:.1f} ms", subtext="Measured local edge execution", col=inf_c3)

    # 5. Clinician Review & Database Signing
    st.subheader("Submit Clinician Diagnostic Review & SQLite Signing")
    
    # Pre-populate review if already stored in database
    v_repo = VisitRepository()
    visit_detail = v_repo.get_visit_detail(visit_id) if visit_id else None
    
    default_ref = st.session_state.get('user_name', 'Dr. Clinician')
    default_status = "CONFIRMED"
    default_notes = ""
    if visit_detail and visit_detail.get('review_status'):
        default_status = visit_detail.get('review_status', 'CONFIRMED')
        default_ref = visit_detail.get('clinician_reference') or default_ref
        default_notes = visit_detail.get('clinical_note') or default_notes

    status_options = ["CONFIRMED", "NEEDS_REVIEW", "UNABLE_TO_DETERMINE"]
    status_idx = status_options.index(default_status) if default_status in status_options else 0

    with st.form("clinician_review_cockpit_form"):
        rev_ref = st.text_input("Clinician Reference ID / Name Signature *", value=default_ref)
        rev_status = st.radio("Diagnostic Review Finding", status_options, index=status_idx, horizontal=True)
        rev_notes = st.text_area("Clinical Notes & Observation Remarks", value=default_notes, placeholder="Enter clinical observations, differential diagnosis remarks, or recommendations...")
        
        submitted = st.form_submit_button("Sign & Save Diagnostic Record to Database", type="primary", use_container_width=True)
        if submitted:
            if not rev_ref.strip():
                st.error("Clinician reference signature is mandatory.")
            else:
                a_repo = AuditRepository()
                success = v_repo.store_clinician_review(visit_id, rev_status, rev_ref.strip(), rev_notes.strip())
                if success:
                    a_repo.log_event('CLINICIAN_REVIEWED', f"CLINICIAN: {rev_ref.strip()}", active_id, visit_id)
                    st.success(f"Review for Visit '{visit_id}' signed and logged to SQLite audit database!")
                    st.rerun()
                else:
                    st.error("Failed to store clinician review.")

    render_disclaimer()
