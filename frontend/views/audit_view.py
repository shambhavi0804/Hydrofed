"""
System Security Audit Log View for HydroFed-ICAF.
"""

import pandas as pd
import streamlit as st
from database.audit_repository import AuditRepository
from frontend.components import render_header, render_disclaimer

def render_audit_view():
    render_header(
        "Local Electronic System Security Audit Log",
        "Cryptographically signed immutable records of patient admissions, CDSS inferences, and clinician signatures."
    )

    a_repo = AuditRepository()
    logs = a_repo.get_logs(limit=100)

    if not logs:
        st.info("No audit logs currently logged in the local SQLite database.")
    else:
        df_l = pd.DataFrame(logs)
        df_l.rename(columns={
            'audit_id': 'Audit ID',
            'timestamp': 'Timestamp',
            'event_type': 'Event Type',
            'actor': 'Actor Signature',
            'patient_id': 'Patient ID',
            'visit_id': 'Visit ID'
        }, inplace=True)
        cols = [c for c in ['Audit ID', 'Timestamp', 'Event Type', 'Actor Signature', 'Patient ID', 'Visit ID'] if c in df_l.columns]
        st.dataframe(df_l[cols], use_container_width=True, hide_index=True)

    render_disclaimer()
