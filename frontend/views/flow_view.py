"""
HydroFed Water-Flow View for HydroFed-ICAF.
"""

import streamlit as st
from frontend.components import render_header, render_disclaimer

def render_flow_view():
    render_header(
        "Water-Flow-Inspired Parameter Pressure Dynamics",
        "Physical model parameter pressure matching where disagreement gradients act as hydrostatic pressure heads."
    )

    flow_levels = st.session_state.get('fl_flow_levels', [0.75, 0.40, 0.60])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <h4 style="margin-top: 0; color: #173B65;">Client-01 (Local Node)</h4>
            <div style="background-color: #F1F5F9; height: 180px; width: 85px; border: 2px solid #CBD5E1; border-radius: 0 0 12px 12px; margin: 15px auto; position: relative; overflow: hidden;">
                <div style="background: linear-gradient(180deg, #2563EB, #0D9488); height: {flow_levels[0]*100}%; width: 100%; position: absolute; bottom: 0; border-radius: 0 0 10px 10px; opacity: 0.85;"></div>
            </div>
            <strong style="color: #2563EB; font-size: 1.1rem;">Fill Level: {flow_levels[0]*100:.1f}%</strong>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <h4 style="margin-top: 0; color: #173B65;">Client-02 (Neighbor Node)</h4>
            <div style="background-color: #F1F5F9; height: 180px; width: 85px; border: 2px solid #CBD5E1; border-radius: 0 0 12px 12px; margin: 15px auto; position: relative; overflow: hidden;">
                <div style="background: linear-gradient(180deg, #2563EB, #0D9488); height: {flow_levels[1]*100}%; width: 100%; position: absolute; bottom: 0; border-radius: 0 0 10px 10px; opacity: 0.85;"></div>
            </div>
            <strong style="color: #2563EB; font-size: 1.1rem;">Fill Level: {flow_levels[1]*100:.1f}%</strong>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <h4 style="margin-top: 0; color: #173B65;">Client-03 (Neighbor Node)</h4>
            <div style="background-color: #F1F5F9; height: 180px; width: 85px; border: 2px solid #CBD5E1; border-radius: 0 0 12px 12px; margin: 15px auto; position: relative; overflow: hidden;">
                <div style="background: linear-gradient(180deg, #2563EB, #0D9488); height: {flow_levels[2]*100}%; width: 100%; position: absolute; bottom: 0; border-radius: 0 0 10px 10px; opacity: 0.85;"></div>
            </div>
            <strong style="color: #2563EB; font-size: 1.1rem;">Fill Level: {flow_levels[2]*100:.1f}%</strong>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="clinical-banner clinical-banner-info">
        💡 <b>Hydrostatic Equilibrium Principle:</b> Connected pipeline valves dynamically equalize weight parameters 
        proportional to communication bandwidth and local dataset divergence.
    </div>
    """, unsafe_allow_html=True)

    render_disclaimer()
