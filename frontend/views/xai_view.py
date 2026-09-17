"""
Explainability (XAI) View for HydroFed-ICAF.
"""

import os
import streamlit as st
from frontend.components import render_header, render_patient_banner, render_disclaimer

def render_xai_view():
    render_header(
        "Explainable AI (XAI) Pathology Saliency Overlays",
        "Grad-CAM and Grad-CAM++ gradient attribution maps from final DenseNet-151 normalization layers."
    )

    res = st.session_state.get("diagnostic_results")
    if not res:
        st.markdown("""
        <div class="clinical-banner clinical-banner-warning">
            ⚠️ <b>No Active Saliency Maps Available</b> — Please execute an X-ray diagnostic analysis to generate explainability heatmaps.
        </div>
        """, unsafe_allow_html=True)
        render_disclaimer()
        return

    active_id = st.session_state.get("active_patient_id", "")
    render_patient_banner(active_id, st.session_state.get("active_patient_data"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("1. Input Radiograph (CLAHE)")
        prep_p = res.get('preprocessed_image_path') or res.get('raw_image_path', '')
        if prep_p and os.path.exists(prep_p):
            st.image(prep_p, caption="Preprocessed Normalized Image", use_container_width=True)
        else:
            st.info("Input image not found.")

    with col2:
        st.subheader("2. Grad-CAM Saliency")
        gcam_p = res.get('gradcam_path', '')
        if gcam_p and os.path.exists(gcam_p):
            st.image(gcam_p, caption="Grad-CAM Pathology Highlight", use_container_width=True)
        else:
            st.info("Grad-CAM visualization unavailable for this inference.")

    with col3:
        st.subheader("3. Grad-CAM++ Saliency")
        gplus_p = res.get('gradcam_plus_path', '')
        if gplus_p and os.path.exists(gplus_p):
            st.image(gplus_p, caption="Grad-CAM++ Fine Granularity Overlay", use_container_width=True)
        else:
            st.info("Grad-CAM++ visualization unavailable for this inference.")

    st.markdown("""
    <div class="clinical-banner clinical-banner-info">
        <b>Explainability Notice:</b> Highlighted heatmaps indicate spatial image regions that contributed to the model's 
        classification score. Explainability visualizations illustrate network gradient salience and do not represent 
        verified anatomical lesion boundaries.
    </div>
    """, unsafe_allow_html=True)

    render_disclaimer()
