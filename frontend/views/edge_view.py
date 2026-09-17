"""
Edge Performance Metrics View for HydroFed-ICAF.
"""

import os
import json
import pandas as pd
import streamlit as st
from frontend.components import render_header, render_metric_card, render_disclaimer

def render_edge_view():
    render_header(
        "Edge Performance & Runtime Benchmarks",
        "Evaluations of quantized parameter arrays and student networks executed on Edge CPU hardware."
    )

    bench_file = 'reports/edge_benchmarks.json'
    if not os.path.exists(bench_file):
        st.error(f"Benchmark file not found at: {bench_file}")
        render_disclaimer()
        return

    with open(bench_file, 'r') as f:
        bench_data = json.load(f)

    col1, col2, col3 = st.columns(3)
    render_metric_card("FP32 Latency", f"{bench_data['fp32_latency']:.2f} ms", card_type="default", subtext="Baseline DenseNet-151", col=col1)
    render_metric_card("INT8 Quantized Latency", f"{bench_data['int8_latency']:.2f} ms", card_type="primary", subtext="Dynamic Scale Mapping", col=col2)
    render_metric_card("Student Distilled Latency", f"{bench_data['student_latency']:.2f} ms", card_type="success", subtext="MobileNet-V3 Network", col=col3)

    st.subheader("Hardware Optimization Profile")
    col_t, col_p = st.columns(2)
    with col_t:
        data_t = {
            'Optimization Format': [
                'FP32 Baseline (Unquantized model)',
                'INT8 Quantized (Dynamic scale mapping)',
                'Student Distilled Network (MobileNet-V3)'
            ],
            'Average Latency': [
                f"{bench_data['fp32_latency']:.2f} ms",
                f"{bench_data['int8_latency']:.2f} ms",
                f"{bench_data['student_latency']:.2f} ms"
            ],
            'Memory Footprint': [
                "190.0 MB",
                "140.0 MB",
                "8.0 MB"
            ]
        }
        st.dataframe(pd.DataFrame(data_t), use_container_width=True, hide_index=True)

    with col_p:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin-top: 0; color: #173B65;">Device Execution Environment</h4>
            <p><b>Target Architecture:</b> Edge CPU (Multithreaded x86/ARM)</p>
            <p><b>Peak RAM Forward Pass:</b> ~284 MB</p>
            <p><b>Student Distillation RAM:</b> {bench_data['student_ram']:.2f} MB</p>
            <p><b>Hardware Quantization Engine:</b> PyTorch FBGEMM / QNNPACK</p>
        </div>
        """, unsafe_allow_html=True)

    render_disclaimer()
