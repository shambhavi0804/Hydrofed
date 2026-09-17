"""
Clinical Report Preview and Dynamic PDF Download View for HydroFed-ICAF.
"""

import streamlit as st
from reports.report_adapter import ReportDataAdapter
from reports.pdf_report import ClinicalPDFReportGenerator
from frontend.components import (
    render_header, render_patient_banner, render_metric_card,
    render_disclaimer
)

def render_report_view():
    render_header(
        "Clinical Decision Support Report & PDF Export",
        "Generate and download institutional clinical reports incorporating multimodal inference and XAI overlays."
    )

    active_id = st.session_state.get("active_patient_id")
    diag_res = st.session_state.get("diagnostic_results")

    if not active_id:
        st.markdown("""
        <div class="clinical-banner clinical-banner-warning">
            ⚠️ <b>No Active Patient Selected</b> — Please select or register a patient profile first.
        </div>
        """, unsafe_allow_html=True)
        render_disclaimer()
        return

    if not diag_res:
        st.markdown("""
        <div class="clinical-banner clinical-banner-warning">
            ⚠️ <b>No Active Diagnostic Evaluation</b> — Run an analysis in <b>X-ray Analysis</b> before generating the clinical report.
        </div>
        """, unsafe_allow_html=True)
        render_disclaimer()
        return

    patient_dem = st.session_state.get("active_patient_data") or {}
    render_patient_banner(active_id, patient_dem)

    # Compile dynamic report data adapter dictionary
    session_meta = {
        'clinician_name': st.session_state.get('user_name', 'Attending Clinician'),
        'edge_node': 'Client-01 (Local Edge AI Node)',
        'clinic_id': 'Local Clinic #01'
    }
    report_data = ReportDataAdapter.build_report_data(
        patient_id=active_id,
        patient_demographics=patient_dem,
        diagnostic_results=diag_res,
        session_metadata=session_meta
    )

    visit_ref = report_data.get('visit_reference', 'V001')
    pdf_filename = f"HydroFed_ICAF_Report_{active_id}_{visit_ref}.pdf"

    st.subheader("Report Summary Preview")
    c1, c2, c3, c4 = st.columns(4)
    pred_t = report_data.get('prediction', 'NORMAL')
    render_metric_card("Report ID", f"{active_id}_{visit_ref}", card_type="default", col=c1)
    render_metric_card("CDSS Prediction", pred_t, card_type="danger" if pred_t == "PNEUMONIA" else "success", col=c2)
    render_metric_card("Pneumonia Probability", report_data.get('pneumonia_probability_pct', '0.00%'), card_type="default", col=c3)
    render_metric_card("Uncertainty", report_data.get('uncertainty_val', '0.0000'), card_type="default", col=c4)

    # PDF Generation Card
    st.markdown("""
    <div class="metric-card metric-card-primary" style="margin: 20px 0;">
        <h3 style="margin-top: 0; color: #173B65;">📄 Dynamic PDF Document Generation</h3>
        <p style="color: #475569; font-size: 0.9rem; margin-bottom: 15px;">
            The PDF report compiles all 6 institutional sections: Patient Profile &amp; Demographics, 
            Multimodal CDSS Classifier Results, Radiological XAI Pathology Heatmaps, Database Verification, 
            Security Audit Trail, and the Mandatory Clinical Disclaimer.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Generate PDF On Demand
    try:
        generator = ClinicalPDFReportGenerator()
        pdf_bytes = generator.generate_pdf(report_data)

        st.download_button(
            label="⬇️ Download PDF Clinical Report",
            data=pdf_bytes,
            file_name=pdf_filename,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Unable to generate the PDF report. Error: {str(e)}")

    # Structured Text Summary Accordion
    with st.expander("🔍 View Raw Clinical Report Schema & Values"):
        st.json(report_data)

    render_disclaimer()
