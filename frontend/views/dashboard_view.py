"""
Dashboard View for HydroFed-ICAF Clinical Decision Support System.
"""

import streamlit as st
import pandas as pd
from database.patient_repository import PatientRepository
from database.schema import get_db_connection
from frontend.components import render_header, render_metric_card, render_disclaimer

def render_dashboard_view():
    render_header(
        "Clinical Decision Support Dashboard",
        "Bio-Inspired Multimodal Radiological Diagnostics & Pediatric EHR Workflow",
        badge_text="Research Prototype",
        badge_type="primary"
    )

    p_count = len(PatientRepository().list_all_patients())
    conn = get_db_connection()
    try:
        diag_count = conn.execute("SELECT COUNT(*) FROM inferences").fetchone()[0]
    except Exception:
        diag_count = 0
    finally:
        conn.close()

    active_id = st.session_state.get("active_patient_id", "") or "None"

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    render_metric_card("Registered Patients", str(p_count), card_type="default", col=col1)
    render_metric_card("X-Ray Evaluations", str(diag_count), card_type="primary", col=col2)
    render_metric_card("Active Patient", active_id, card_type="success" if active_id != "None" else "warning", col=col3)
    render_metric_card("Edge Node Status", "Client-01 (Ready)", card_type="default", col=col4)

    # Workflow Stepper
    st.subheader("Clinical Decision Support Workflow")
    st.markdown("""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; text-align: center;">
            <div style="padding: 10px; background: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0;">
                <div style="font-weight: 700; color: #2563EB; font-size: 0.85rem;">STEP 1</div>
                <div style="font-size: 0.82rem; color: #1E293B; margin-top: 2px;">Patient Selection</div>
            </div>
            <div style="padding: 10px; background: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0;">
                <div style="font-weight: 700; color: #2563EB; font-size: 0.85rem;">STEP 2</div>
                <div style="font-size: 0.82rem; color: #1E293B; margin-top: 2px;">Clinical Inputs</div>
            </div>
            <div style="padding: 10px; background: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0;">
                <div style="font-weight: 700; color: #2563EB; font-size: 0.85rem;">STEP 3</div>
                <div style="font-size: 0.82rem; color: #1E293B; margin-top: 2px;">X-Ray Upload</div>
            </div>
            <div style="padding: 10px; background: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0;">
                <div style="font-weight: 700; color: #2563EB; font-size: 0.85rem;">STEP 4</div>
                <div style="font-size: 0.82rem; color: #1E293B; margin-top: 2px;">Run CDSS Inference</div>
            </div>
            <div style="padding: 10px; background: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0;">
                <div style="font-weight: 700; color: #2563EB; font-size: 0.85rem;">STEP 5</div>
                <div style="font-size: 0.82rem; color: #1E293B; margin-top: 2px;">Review Saliency / XAI</div>
            </div>
            <div style="padding: 10px; background: #F8FAFC; border-radius: 6px; border: 1px solid #E2E8F0;">
                <div style="font-weight: 700; color: #2563EB; font-size: 0.85rem;">STEP 6</div>
                <div style="font-size: 0.82rem; color: #1E293B; margin-top: 2px;">Download PDF Report</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Current Session Evaluation Cockpit
    diag_res = st.session_state.get("diagnostic_results")
    if diag_res:
        st.subheader("Current Session Evaluation")
        pred_text = "PNEUMONIA" if diag_res.get("predicted_class") == 1 else "NORMAL"
        card_t = "danger" if diag_res.get("predicted_class") == 1 else "success"
        
        c1, c2, c3, c4 = st.columns(4)
        render_metric_card("Primary Prediction", pred_text, card_type=card_t, col=c1)
        render_metric_card("Pneumonia Prob.", f"{diag_res.get('pneumonia_probability', 0.0):.2%}", card_type="default", col=c2)
        render_metric_card("Model Confidence", f"{diag_res.get('confidence', 0.0):.2%}", card_type="default", col=c3)
        render_metric_card("Uncertainty (MC Std)", f"{diag_res.get('uncertainty', 0.0):.4f}", card_type="warning" if diag_res.get('uncertainty', 0.0) > 0.15 else "default", col=c4)
    else:
        st.markdown("""
        <div class="clinical-banner clinical-banner-info">
            💡 <b>Workspace Ready:</b> Navigate to <b>Patient Registration / Search</b> or <b>X-ray Analysis</b> to run a clinical assessment.
        </div>
        """, unsafe_allow_html=True)

    render_disclaimer()
