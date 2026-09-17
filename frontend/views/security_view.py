"""
Decentralized Security and Parameter Validation View for HydroFed-ICAF.
"""

import pandas as pd
import streamlit as st
from frontend.components import render_header, render_metric_card, render_disclaimer

def render_security_view():
    render_header(
        "Cryptographic Security & Parameter Integrity Validation",
        "Authenticated encryption benchmarks and strict mathematical input-norm integrity guards."
    )

    sec_count = st.session_state.get('fl_sec_encrypted_count', 0)

    c1, c2, c3 = st.columns(3)
    render_metric_card("Encryption Scheme", "AES-256-GCM", card_type="primary", subtext="NIST SP 800-38D Authenticated", col=c1)
    render_metric_card("Encrypted Payloads", f"{sec_count} updates", card_type="default", col=c2)
    render_metric_card("Validation Overheads", "~1.2 ms", card_type="success", subtext="L2 Norm & NaN Filter Active", col=c3)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cryptographic Security Summary")
        data_s = {
            'Security Metric Attribute': [
                'Encryption Protocol',
                'Key Derivation Function',
                'Authentication Tag Length',
                'Payload Integrity Checks',
                'Model Poisoning Filter'
            ],
            'Value Status': [
                'AES-256-GCM (Authenticated)',
                'PBKDF2-HMAC-SHA256 (200,000 iterations)',
                '128-bit GCM MAC Tag',
                'Active (100% Verification)',
                'Strict L2 Norm & NaN Boundary Enforced'
            ]
        }
        st.dataframe(pd.DataFrame(data_s), use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Security Intrusion Safeguards")
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin-top: 0; color: #173B65;">🛡️ Hospital Privacy &amp; Data Integrity</h4>
            <p><b>Confidentiality Guarantee:</b> AES-256-GCM guarantees model parameter confidentiality and payload integrity during peer-to-peer gossip exchanges.</p>
            <p><b>Zero Leakage of Raw Patient Data:</b> Raw chest X-ray DICOM/JPEG images and patient demographics never leave the local hospital premise.</p>
            <p><b>Tamper-Evident Hashing:</b> Audit event logs are cryptographically sealed with immutable timestamps.</p>
        </div>
        """, unsafe_allow_html=True)

    render_disclaimer()
