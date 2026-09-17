"""
Patient Registration and Search View for HydroFed-ICAF.
"""

import os
import pandas as pd
import streamlit as st
from database.patient_repository import PatientRepository
from database.visit_repository import VisitRepository
from database.audit_repository import AuditRepository
from frontend.components import render_header, render_patient_banner, render_disclaimer

def render_patient_view():
    render_header(
        "Electronic Health Records (EHR) Patient Management",
        "Register new clinical patient profiles or search existing institutional hospital records."
    )

    tab_search, tab_reg = st.tabs(["🔍 Search & Select Patient", "📝 Register New Patient"])

    # =========================================================================
    # TAB 1: PATIENT SEARCH & SELECTION
    # =========================================================================
    with tab_search:
        st.subheader("Query Local Clinical Database")
        search_q = st.text_input("Search Patient Identifier", placeholder="Enter full or partial Patient ID (e.g., person100, normal_0001)")
        
        p_repo = PatientRepository()
        all_patients = p_repo.list_all_patients()
        
        if search_q:
            filtered = [p for p in all_patients if search_q.lower() in p['patient_id'].lower()]
        else:
            filtered = all_patients

        if not filtered:
            st.warning("No matching patient records found in local SQLite database.")
        else:
            df_p = pd.DataFrame(filtered)
            df_p.rename(columns={'patient_id': 'Patient ID', 'created_at': 'Registration Date', 'status': 'Status'}, inplace=True)
            st.dataframe(df_p, use_container_width=True, hide_index=True)
            
            p_ids = [p['patient_id'] for p in filtered]
            current_active = st.session_state.get("active_patient_id", "")
            default_idx = p_ids.index(current_active) if current_active in p_ids else 0
            
            selected_pat_id = st.selectbox("Select Patient to Set as Active", p_ids, index=default_idx)
            
            if st.button("Set Selected Patient as Active", type="primary", use_container_width=True):
                st.session_state.active_patient_id = selected_pat_id
                
                # Fetch baseline clinical observation from synthetic CSV or database visits
                age, gender, diabetes, smoke, family = 5.0, "Male", 0, 0, 0
                synthetic_csv = 'reports/synthetic_patients_clinical.csv'
                if os.path.exists(synthetic_csv):
                    try:
                        df_synth = pd.read_csv(synthetic_csv)
                        match = df_synth[df_synth['patient_id'] == selected_pat_id]
                        if not match.empty:
                            row = match.iloc[0]
                            age = float(row.get('age', 5.0))
                            gender = str(row.get('gender', 'Male'))
                            diabetes = int(row.get('diabetes', 0))
                            smoke = int(row.get('passive_smoke_exposure', 0))
                            family = int(row.get('family_respiratory_history', 0))
                    except Exception:
                        pass
                else:
                    v_repo = VisitRepository()
                    hist = v_repo.get_visit_history(selected_pat_id)
                    if hist:
                        latest = hist[-1]
                        age = float(latest.get('age', 5.0))
                        gender = str(latest.get('gender', 'Male'))
                        diabetes = int(latest.get('diabetes', 0))
                        smoke = int(latest.get('passive_smoke_exposure', 0))
                        family = int(latest.get('family_respiratory_history', 0))

                st.session_state.active_patient_data = {
                    'age': age,
                    'gender': gender,
                    'diabetes': diabetes,
                    'passive_smoke_exposure': smoke,
                    'family_respiratory_history': family
                }
                st.success(f"Active clinical workspace shifted to Patient '{selected_pat_id}'.")
                st.rerun()

    # =========================================================================
    # TAB 2: REGISTER NEW PATIENT
    # =========================================================================
    with tab_reg:
        st.subheader("Record New Patient Demographics")
        with st.form("new_patient_registration_form"):
            c_id1, c_id2 = st.columns(2)
            with c_id1:
                reg_id = st.text_input("Patient Unique ID *", placeholder="e.g., clinic_patient_800")
            with c_id2:
                reg_name = st.text_input("Patient Full Name (Optional)", placeholder="e.g., Alex Johnson")

            col1, col2 = st.columns(2)
            with col1:
                reg_age = st.slider("Patient Age (Years)", min_value=0.1, max_value=90.0, value=5.0, step=0.1)
                reg_gender = st.selectbox("Biological Gender", ["Male", "Female"])
                reg_diabetes = st.selectbox("Comorbidity: Diabetes Mellitus", ["Absent", "Present"])
            with col2:
                reg_smoke = st.selectbox("Environmental Exposure: Passive Smoke", ["No", "Yes"])
                reg_family = st.selectbox("Genetic History: Family Respiratory History", ["No", "Yes"])
                reg_bp = st.text_input("Blood Pressure (mmHg)", value="105/70")

            submitted = st.form_submit_button("Register Patient Locally", type="primary", use_container_width=True)
            if submitted:
                if not reg_id.strip():
                    st.error("Please provide a valid Patient Unique ID.")
                else:
                    p_repo = PatientRepository()
                    v_repo = VisitRepository()
                    a_repo = AuditRepository()
                    
                    if p_repo.patient_exists(reg_id.strip()):
                        st.error(f"Patient ID '{reg_id.strip()}' already exists in database.")
                    else:
                        success = p_repo.register_patient(reg_id.strip())
                        if success:
                            visit_id = f"{reg_id.strip()}-V001"
                            v_repo.create_visit(visit_id, reg_id.strip(), 'Client-01', 'v1.0')
                            v_repo.store_clinical_observation(
                                visit_id=visit_id,
                                age=reg_age,
                                gender=reg_gender,
                                diabetes=1 if reg_diabetes == "Present" else 0,
                                smoke=1 if reg_smoke == "Yes" else 0,
                                family=1 if reg_family == "Yes" else 0
                            )
                            a_repo.log_event('PATIENT_REGISTERED', st.session_state.get('user_name', 'CLINICIAN'), reg_id.strip(), visit_id)
                            
                            st.session_state.active_patient_id = reg_id.strip()
                            st.session_state.active_patient_data = {
                                'patient_name': reg_name.strip() if reg_name.strip() else f"Patient {reg_id.strip()}",
                                'age': reg_age,
                                'gender': reg_gender,
                                'diabetes': 1 if reg_diabetes == "Present" else 0,
                                'passive_smoke_exposure': 1 if reg_smoke == "Yes" else 0,
                                'family_respiratory_history': 1 if reg_family == "Yes" else 0,
                                'blood_pressure': reg_bp
                            }
                            st.success(f"Patient '{reg_id.strip()}' registered successfully and set as active patient!")
                            st.rerun()
                        else:
                            st.error("Failed to register patient in database.")

    st.markdown("<br>", unsafe_allow_html=True)
    render_disclaimer()
