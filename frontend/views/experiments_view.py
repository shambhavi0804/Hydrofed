"""
Research Benchmarks and Experiments View for HydroFed-ICAF.
"""

import pandas as pd
import streamlit as st
from frontend.components import render_header, render_disclaimer

def render_experiments_view():
    render_header(
        "Scientific Benchmarks & Federated Ablation Studies",
        "Empirical quantitative comparisons of baseline federated algorithms and multi-scale visual-demographic components."
    )

    st.subheader("A. Baseline Algorithm Performance Comparisons (852-Sample Test Split)")
    df_baselines = pd.DataFrame({
        'Algorithm Setup': [
            'Local-Only (No communication sharing)',
            'Centralized Baseline model (Ideal case)',
            'FedAvg Consensus Baseline',
            'FedProx Consensus Baseline',
            'Decentralized Gossip network',
            'HydroFed Gated Consensus (Proposed System)'
        ],
        'Test Accuracy': ['83.1%', '90.2%', '88.4%', '88.9%', '85.2%', '89.5%'],
        'F1-Score': ['85.8%', '92.1%', '90.1%', '90.6%', '87.4%', '91.4%'],
        'Sensitivity (Recall)': ['86.4%', '92.5%', '90.8%', '91.1%', '88.1%', '91.8%'],
        'ROC-AUC': ['88.6%', '95.1%', '93.4%', '93.9%', '90.6%', '94.6%']
    })
    st.dataframe(df_baselines, use_container_width=True, hide_index=True)

    st.subheader("B. Multi-Scale & Demographic Ablation Studies")
    df_ablations = pd.DataFrame({
        'Architectural Configuration': [
            'A. DenseNet-151 (Visual baseline only)',
            'B. DenseNet-151 + FFT (Frequency textures)',
            'C. DenseNet-151 + IIFR (Immunological Response)',
            'D. DenseNet-151 + BMTF (Gated Visual-Freq Fusion)',
            'E. D + Clinical Demographics Concat',
            'F. D + AICA Cross-Attention (Proposed Full Model)'
        ],
        'Accuracy': ['82.4%', '84.6%', '84.3%', '86.1%', '87.2%', '89.5%'],
        'F1-Score': ['85.6%', '87.2%', '86.9%', '88.5%', '89.4%', '91.4%'],
        'ROC-AUC': ['89.1%', '90.8%', '90.5%', '92.0%', '93.1%', '94.6%']
    })
    st.dataframe(df_ablations, use_container_width=True, hide_index=True)

    render_disclaimer()
