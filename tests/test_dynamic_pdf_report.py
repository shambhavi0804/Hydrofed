"""
Comprehensive Automated Verification Test for Dynamic Clinical PDF Reports and Frontend Modules.
"""

import os
import sys
import io

# Add workspace root to Python path
sys.path.append(os.getcwd())

from reports.report_adapter import ReportDataAdapter
from reports.pdf_report import ClinicalPDFReportGenerator
from database.schema import init_database
from database.patient_repository import PatientRepository
from database.visit_repository import VisitRepository
from database.audit_repository import AuditRepository

def test_dynamic_pdf_generation():
    print("================================================================")
    print("RUNNING DYNAMIC PDF REPORT VERIFICATION TESTS")
    print("================================================================")

    init_database()
    p_repo = PatientRepository()
    v_repo = VisitRepository()
    a_repo = AuditRepository()

    # TEST CASE 1: Patient Alpha (NORMAL Case)
    pat_a_id = "TEST_PATIENT_ALPHA"
    p_repo.register_patient(pat_a_id)
    v_repo.create_visit(f"{pat_a_id}-V101", pat_a_id, "Client-01", "v1.0")
    v_repo.store_clinical_observation(f"{pat_a_id}-V101", 3.5, "Female", 0, 0, 0)
    v_repo.store_inference(f"{pat_a_id}-V101", 0, 0.098, 0.902, 0.031, 0.145)
    v_repo.store_clinician_review(f"{pat_a_id}-V101", "CONFIRMED", "Dr. Elena Rostova", "Clear lung fields, no radiological abnormality.")
    a_repo.log_event("INFERENCE_COMPLETED", "Dr. Elena Rostova", pat_a_id, f"{pat_a_id}-V101")

    demographics_a = {
        'patient_name': "Baby Alpha",
        'age': 3.5,
        'gender': "Female",
        'diabetes': 0,
        'passive_smoke_exposure': 0,
        'family_respiratory_history': 0,
        'blood_pressure': "95/60 mmHg",
        'fasting_blood_sugar': "82 mg/dL",
        'height': "98 cm",
        'weight': "14.2 kg"
    }

    diag_a = {
        'visit_id': f"{pat_a_id}-V101",
        'predicted_class': 0,
        'pneumonia_probability': 0.098,
        'confidence': 0.902,
        'uncertainty': 0.031,
        'total_cdss_latency': 0.145,
        'raw_image_path': 'reports/uploaded_xray.jpeg',
        'preprocessed_image_path': 'reports/uploaded_xray.jpeg',
        'gradcam_path': 'reports/xai_outputs/10-V656_gradcam.png' if os.path.exists('reports/xai_outputs/10-V656_gradcam.png') else '',
        'gradcam_plus_path': 'reports/xai_outputs/10-V656_gradcam_plus.png' if os.path.exists('reports/xai_outputs/10-V656_gradcam_plus.png') else '',
        'clinical_data': demographics_a
    }

    report_data_a = ReportDataAdapter.build_report_data(
        patient_id=pat_a_id,
        patient_demographics=demographics_a,
        diagnostic_results=diag_a,
        session_metadata={'clinician_name': "Dr. Elena Rostova", 'edge_node': "Client-01"}
    )

    gen = ClinicalPDFReportGenerator()
    pdf_bytes_a = gen.generate_pdf(report_data_a)
    assert len(pdf_bytes_a) > 10000, "Patient Alpha PDF generation failed (size too small)"
    assert report_data_a['prediction'] == "NORMAL", "Patient Alpha prediction must be NORMAL"
    assert report_data_a['pneumonia_probability_pct'] == "9.80%", "Patient Alpha prob mismatch"
    assert report_data_a['signed_by'] == "Dr. Elena Rostova", "Patient Alpha signer mismatch"
    print(f"[PASS] TEST 1: Patient Alpha (NORMAL) generated valid PDF of {len(pdf_bytes_a):,} bytes")

    # TEST CASE 2: Patient Beta (PNEUMONIA Case)
    pat_b_id = "TEST_PATIENT_BETA"
    p_repo.register_patient(pat_b_id)
    v_repo.create_visit(f"{pat_b_id}-V202", pat_b_id, "Client-01", "v1.0")
    v_repo.store_clinical_observation(f"{pat_b_id}-V202", 68.0, "Male", 1, 1, 1)
    v_repo.store_inference(f"{pat_b_id}-V202", 1, 0.942, 0.942, 0.065, 0.230)
    v_repo.store_clinician_review(f"{pat_b_id}-V202", "CONFIRMED", "Dr. Marcus Vance", "Severe right middle/lower lobe consolidation. Prescribed IV antibiotics.")
    a_repo.log_event("INFERENCE_COMPLETED", "Dr. Marcus Vance", pat_b_id, f"{pat_b_id}-V202")

    demographics_b = {
        'patient_name': "Elderly Beta",
        'age': 68.0,
        'gender': "Male",
        'diabetes': 1,
        'passive_smoke_exposure': 1,
        'family_respiratory_history': 1,
        'blood_pressure': "145/92 mmHg",
        'fasting_blood_sugar': "164 mg/dL",
        'height': "175 cm",
        'weight': "82.0 kg"
    }

    diag_b = {
        'visit_id': f"{pat_b_id}-V202",
        'predicted_class': 1,
        'pneumonia_probability': 0.942,
        'confidence': 0.942,
        'uncertainty': 0.065,
        'total_cdss_latency': 0.230,
        'raw_image_path': 'reports/uploaded_xray.jpeg',
        'preprocessed_image_path': 'reports/uploaded_xray.jpeg',
        'gradcam_path': 'reports/xai_outputs/TRI123-V324_gradcam.png' if os.path.exists('reports/xai_outputs/TRI123-V324_gradcam.png') else '',
        'gradcam_plus_path': 'reports/xai_outputs/TRI123-V324_gradcam_plus.png' if os.path.exists('reports/xai_outputs/TRI123-V324_gradcam_plus.png') else '',
        'clinical_data': demographics_b
    }

    report_data_b = ReportDataAdapter.build_report_data(
        patient_id=pat_b_id,
        patient_demographics=demographics_b,
        diagnostic_results=diag_b,
        session_metadata={'clinician_name': "Dr. Marcus Vance", 'edge_node': "Client-01"}
    )

    pdf_bytes_b = gen.generate_pdf(report_data_b)
    assert len(pdf_bytes_b) > 10000, "Patient Beta PDF generation failed (size too small)"
    assert report_data_b['prediction'] == "PNEUMONIA", "Patient Beta prediction must be PNEUMONIA"
    assert report_data_b['pneumonia_probability_pct'] == "94.20%", "Patient Beta prob mismatch"
    assert report_data_b['signed_by'] == "Dr. Marcus Vance", "Patient Beta signer mismatch"
    print(f"[PASS] TEST 2: Patient Beta (PNEUMONIA) generated valid PDF of {len(pdf_bytes_b):,} bytes")

    # TEST CASE 3: Cross-contamination check
    assert report_data_a['patient_id'] != report_data_b['patient_id']
    assert report_data_a['prediction'] != report_data_b['prediction']
    assert report_data_a['pneumonia_probability_pct'] != report_data_b['pneumonia_probability_pct']
    assert report_data_a['signed_by'] != report_data_b['signed_by']
    print("[PASS] TEST 3: Dynamic data isolation confirmed (No static values or cross-patient contamination)")

    print("================================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("================================================================")

if __name__ == '__main__':
    test_dynamic_pdf_generation()
