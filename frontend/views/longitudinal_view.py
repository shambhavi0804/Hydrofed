"""
Longitudinal View and Patient History for HydroFed-ICAF.
"""

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from database.visit_repository import VisitRepository
from cdss.longitudinal_engine import LongitudinalTrendEngine
from frontend.components import (
    render_header, render_patient_banner, render_metric_card,
    setup_matplotlib_clinical_theme, render_disclaimer
)

def render_longitudinal_view():
    render_header(
        "Longitudinal Patient History & Temporal Analysis",
        "Tracks trajectory of CDSS classification probabilities, confidence, and uncertainty across historical clinic visits."
    )

    active_id = st.session_state.get("active_patient_id")
    if not active_id:
        st.markdown("""
        <div class="clinical-banner clinical-banner-warning">
            ⚠️ <b>No Active Patient Loaded</b> — Please look up or select an active patient profile.
        </div>
        """, unsafe_allow_html=True)
        render_disclaimer()
        return

    render_patient_banner(active_id, st.session_state.get("active_patient_data"))

    v_repo = VisitRepository()
    visits = v_repo.get_visit_history(active_id)

    if not visits:
        st.warning("No historical clinic visits logged for this patient yet.")
        render_disclaimer()
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Longitudinal Probability Timeline")
        setup_matplotlib_clinical_theme()
        fig, ax = plt.subplots(figsize=(6, 3.8))

        dates = [pd.to_datetime(v['visit_timestamp']) for v in visits]
        probs = [float(v.get('pneumonia_probability') or 0.0) for v in visits]
        confs = [float(v.get('confidence') or 0.0) for v in visits]
        uncs = [float(v.get('uncertainty') or 0.0) for v in visits]

        ax.plot(dates, probs, marker='o', color='#DC2626', linewidth=2.0, label='Pneumonia Prob.')
        ax.plot(dates, confs, marker='s', color='#16A34A', linewidth=1.5, linestyle='--', label='Confidence')
        ax.plot(dates, uncs, marker='^', color='#D97706', linewidth=1.5, linestyle=':', label='Uncertainty')

        ax.set_ylim(-0.05, 1.05)
        ax.set_ylabel("Diagnostic Index Score")
        ax.legend(loc='upper right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E1')
        fig.autofmt_xdate()
        st.pyplot(fig)

    with col2:
        st.subheader("Longitudinal Trend Engine Output")
        engine = LongitudinalTrendEngine()
        trend_res = engine.analyze_trend(visits)

        trend_status = trend_res.get('trend', 'STABLE')
        trend_color = "primary"
        if trend_status == 'IMPROVING':
            trend_color = "success"
        elif trend_status == 'WORSENING':
            trend_color = "danger"

        render_metric_card(
            "Temporal Trend Decision",
            trend_status,
            card_type=trend_color,
            subtext=trend_res.get('message', '')
        )

        if trend_res.get('warning'):
            st.markdown(f"""
            <div class="clinical-banner clinical-banner-warning">
                ⚠️ <b>Longitudinal Warning:</b> {trend_res['warning']}
            </div>
            """, unsafe_allow_html=True)

    st.subheader("Historical Visit Timeline Log")
    df_v = pd.DataFrame(visits)
    if not df_v.empty:
        cols_to_show = ['visit_timestamp', 'pneumonia_probability', 'uncertainty', 'confidence', 'review_status', 'clinical_note']
        available_cols = [c for c in cols_to_show if c in df_v.columns]
        df_show = df_v[available_cols].copy()
        df_show.rename(columns={
            'visit_timestamp': 'Visit Date/Time',
            'pneumonia_probability': 'Pneumonia Prob.',
            'uncertainty': 'Uncertainty',
            'confidence': 'Confidence',
            'review_status': 'Review Status',
            'clinical_note': 'Clinical Notes'
        }, inplace=True)
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    render_disclaimer()
