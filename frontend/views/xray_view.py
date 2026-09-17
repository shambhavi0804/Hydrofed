"""
Radiological X-ray Analysis View for HydroFed-ICAF.
"""

import os
import time
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
from database.visit_repository import VisitRepository
from database.audit_repository import AuditRepository
from frontend.components import render_header, render_patient_banner, render_disclaimer

def render_xray_view(inference_service):
    render_header(
        "Radiological Chest X-ray Pipeline Configurator",
        "Upload pediatric/adult chest radiographs or select preset test scans to execute multimodal diagnostics."
    )

    active_id = st.session_state.get("active_patient_id")
    if not active_id:
        st.markdown("""
        <div class="clinical-banner clinical-banner-warning">
            ⚠️ <b>No Active Patient Selected</b> — Please select or register a patient profile in the <b>Patient Registration / Search</b> page before executing diagnostics.
        </div>
        """, unsafe_allow_html=True)
        render_disclaimer()
        return

    render_patient_banner(active_id, st.session_state.get("active_patient_data"))

    # Locate available presets or fallback images
    preset_candidates = [
        {"path": "reports/uploaded_xray.jpeg", "label": "Default Hospital Test Case"},
        {"path": "archive (4)/chest_xray/test/NORMAL/IM-0028-0001.jpeg", "label": "NORMAL Case 1"},
        {"path": "archive (4)/chest_xray/test/NORMAL/IM-0029-0001.jpeg", "label": "NORMAL Case 2"},
        {"path": "archive (4)/chest_xray/test/PNEUMONIA/person100_bacteria_482.jpeg", "label": "BACTERIA Case 1"},
        {"path": "archive (4)/chest_xray/test/PNEUMONIA/person116_virus_221.jpeg", "label": "VIRUS Case 1"}
    ]
    available_presets = [c for c in preset_candidates if os.path.exists(c["path"])]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Configure Radiological Scan")
        
        selected_preset_path = None
        if available_presets:
            preset_labels = ["-- Choose Preset Test Scan --"] + [f"{c['label']} ({os.path.basename(c['path'])})" for c in available_presets]
            preset_choice = st.selectbox("Preset Radiograph Library", range(len(preset_labels)), format_func=lambda x: preset_labels[x])
            if preset_choice > 0:
                selected_preset_path = available_presets[preset_choice - 1]["path"]

        st.markdown("<div style='text-align: center; margin: 10px 0; color: #64748B; font-weight: 600;'>— OR —</div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Custom DICOM/JPEG Image", type=['jpeg', 'jpg', 'png'])

    with col2:
        st.subheader("2. Pre-inference Visualizer")
        target_image_path = None
        custom_image_bytes = None

        if uploaded_file is not None:
            custom_image_bytes = uploaded_file.read()
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Chest X-ray", use_container_width=True)
        elif selected_preset_path:
            target_image_path = selected_preset_path
            st.image(target_image_path, caption=f"Selected Preset: {os.path.basename(target_image_path)}", use_container_width=True)
        else:
            st.markdown("""
            <div style="background: #F8FAFC; border: 2px dashed #CBD5E1; border-radius: 8px; height: 260px; display: flex; align-items: center; justify-content: center; color: #64748B; text-align: center; padding: 20px;">
                No radiograph configured yet.<br>Select a preset scan or upload a custom X-ray file.
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 20px 0; border-color: #E2E8F0;'/>", unsafe_allow_html=True)

    if st.button("🚀 Execute Multimodal Diagnostics Pipeline", type="primary", use_container_width=True):
        if not target_image_path and not custom_image_bytes:
            st.error("Please configure an input radiograph (preset or upload) before running diagnostics.")
        else:
            with st.spinner("Executing BMTF-IIFR visual-frequency processing & AICA cross-attention diagnostics..."):
                os.makedirs('reports/xai_outputs', exist_ok=True)
                filepath = 'reports/uploaded_xray.jpeg'
                if custom_image_bytes:
                    with open(filepath, 'wb') as f:
                        f.write(custom_image_bytes)
                else:
                    filepath = target_image_path

                # Load clinical demographics
                pat_id = st.session_state.active_patient_id
                data_dem = st.session_state.get("active_patient_data") or {}

                age = float(data_dem.get('age', 5.0))
                gender = str(data_dem.get('gender', 'Male'))
                diabetes = int(data_dem.get('diabetes', 0))
                smoke = int(data_dem.get('passive_smoke_exposure', 0))
                family = int(data_dem.get('family_respiratory_history', 0))

                # Normalize 5-dim clinical vector for neural network
                age_norm = age / 80.0
                gender_val = 1.0 if gender == 'Female' else 0.0
                clinical_vector = [age_norm, gender_val, float(diabetes), float(smoke), float(family)]

                visit_id = f"{pat_id}-V{int(time.time()) % 1000:03d}"

                # Run backend CDSS inference (UNCHANGED BACKEND)
                res = inference_service.run_cdss_diagnostics(
                    image_path=filepath,
                    clinical_vector=clinical_vector,
                    output_vis_dir='reports/xai_outputs',
                    visit_id=visit_id
                )

                # Generate CLAHE normalized visual
                prep_vis_path = f"reports/xai_outputs/{visit_id}_preprocessed.png"
                try:
                    raw_img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                    if raw_img is not None:
                        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                        clahe_img = clahe.apply(raw_img)
                        h, w = clahe_img.shape[:2]
                        scale = min(224 / w, 224 / h)
                        new_w, new_h = int(w * scale), int(h * scale)
                        resized = cv2.resize(clahe_img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
                        padded = np.zeros((224, 224), dtype=np.uint8)
                        x_offset = (224 - new_w) // 2
                        y_offset = (224 - new_h) // 2
                        padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                        cv2.imwrite(prep_vis_path, padded)
                    else:
                        prep_vis_path = filepath
                except Exception:
                    prep_vis_path = filepath

                # Write to SQLite database
                v_repo = VisitRepository()
                a_repo = AuditRepository()

                v_repo.create_visit(visit_id, pat_id, 'Client-01', 'v1.0')
                v_repo.store_clinical_observation(visit_id, age, gender, diabetes, smoke, family)
                v_repo.store_inference(
                    visit_id=visit_id,
                    predicted_class=res['predicted_class'],
                    prob=res['pneumonia_probability'],
                    confidence=res['confidence'],
                    uncertainty=res['uncertainty'],
                    latency=res['total_cdss_latency']
                )
                v_repo.store_xai_result(visit_id, 'Grad-CAM', res['gradcam_heatmap_path'])
                v_repo.store_xai_result(visit_id, 'Grad-CAM++', res['gradcam_plus_heatmap_path'])

                a_repo.log_event('INFERENCE_COMPLETED', st.session_state.get('user_name', 'CLINICIAN'), pat_id, visit_id)

                # Save diagnostic results into session state
                st.session_state.diagnostic_results = {
                    'visit_id': visit_id,
                    'predicted_class': res['predicted_class'],
                    'pneumonia_probability': res['pneumonia_probability'],
                    'confidence': res['confidence'],
                    'uncertainty': res['uncertainty'],
                    'total_cdss_latency': res['total_cdss_latency'],
                    'raw_image_path': filepath,
                    'preprocessed_image_path': prep_vis_path,
                    'gradcam_path': res['gradcam_heatmap_path'],
                    'gradcam_plus_path': res['gradcam_plus_heatmap_path'],
                    'clinical_data': {
                        'age': age,
                        'gender': gender,
                        'diabetes': diabetes,
                        'passive_smoke_exposure': smoke,
                        'family_respiratory_history': family
                    }
                }

                st.success("Diagnostics executed successfully! Navigate to **CDSS Results** or **Explainability** to inspect findings.")
                st.rerun()

    render_disclaimer()
