"""
Model Architecture Specifications View for HydroFed-ICAF.
"""

import pandas as pd
import streamlit as st
from frontend.components import render_header, render_disclaimer

def render_model_view():
    render_header(
        "HydroFed-ICAF Neural Architecture Specifications",
        "Detailed layer dimensions, tensor representations, and multimodal fusion topology."
    )

    df_model = pd.DataFrame({
        'Component Layer Name': [
            'Input Chest X-Ray Map',
            'DenseNet-151 Semantic Backbone',
            'BMTF Multi-Scale Gated Fusion',
            'Clinical Demographics Tokens',
            'AICA Attention Matrix Map',
            'CDSS Logic Classifier Logits'
        ],
        'Tensor Dimensions Shape': [
            '[Batch Size, 3, 224, 224]',
            '[Batch Size, 1264, 7, 7]',
            '[Batch Size, 128, 7, 7]',
            '[Batch Size, 5, 128]',
            '[Batch Size, 128, 7, 7]',
            '[Batch Size, 2]'
        ],
        'Functional Layer Description': [
            'Preprocessed normalized gray-value chest scans',
            'Visual feature representations from final dense block norm layer',
            'Gated channel-wise balance of spatial visuals and FFT frequency textures',
            'EHR embeddings (Age, Gender, Diabetes, Smoke, Family)',
            'Gated demographics-visual cross-attention mappings',
            'Predicted normal vs pneumonia probability logits'
        ]
    })
    st.dataframe(df_model, use_container_width=True, hide_index=True)

    render_disclaimer()
