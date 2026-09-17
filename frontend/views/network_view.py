"""
Decentralized Network Gossip View for HydroFed-ICAF.
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from database.audit_repository import AuditRepository
from frontend.components import (
    render_header, render_metric_card, setup_matplotlib_clinical_theme,
    render_disclaimer
)

def render_network_view(get_runner_func):
    render_header(
        "Decentralized Small-World Federated Topology",
        "Simulates gossip consensus across 60 isolated clinic nodes exchanging encrypted model parameter updates."
    )

    if 'fl_round' not in st.session_state:
        st.session_state.fl_round = 0
    if 'fl_consensus_history' not in st.session_state:
        st.session_state.fl_consensus_history = []
    if 'fl_flow_levels' not in st.session_state:
        st.session_state.fl_flow_levels = [0.75, 0.40, 0.60]
    if 'fl_sec_encrypted_count' not in st.session_state:
        st.session_state.fl_sec_encrypted_count = 0

    c1, c2, c3 = st.columns(3)
    render_metric_card("Communication Round", str(st.session_state.fl_round), card_type="primary", col=c1)
    render_metric_card("Total Nodes", "60 Clinics", card_type="default", subtext="Small-World Graph Topology", col=c2)
    latest_err = f"{st.session_state.fl_consensus_history[-1]:.4f}" if st.session_state.fl_consensus_history else "0.0500"
    render_metric_card("Consensus Error", latest_err, card_type="default", col=c3)

    if st.button("🔄 Advance Decentralized Gossip Round", type="primary", use_container_width=True):
        with st.spinner("Executing gossip communication and secure parameter exchanges..."):
            runner = get_runner_func()
            test_metrics, consensus_errors = runner.run_decentralized_hydrofed(rounds=1)
            err = float(consensus_errors[-1]) if len(consensus_errors) > 0 else 0.05
            
            st.session_state.fl_round += 1
            st.session_state.fl_consensus_history.append(err)
            
            # Update flow levels
            avg = 0.58
            for i in range(len(st.session_state.fl_flow_levels)):
                curr = st.session_state.fl_flow_levels[i]
                st.session_state.fl_flow_levels[i] = curr + 0.5 * (avg - curr) + (np.random.rand() - 0.5) * 0.02
                
            st.session_state.fl_sec_encrypted_count += 60
            
            # Log audit events
            a_repo = AuditRepository()
            a_repo.log_event('FL_UPDATE_SENT', 'FL_CLIENT', None, None)
            a_repo.log_event('MODEL_UPDATED', 'HYDROFED_ENGINE', None, None)
            
            st.success(f"Gossip communication completed successfully for Round {st.session_state.fl_round}!")
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Network Topology Graph")
        setup_matplotlib_clinical_theme()
        fig, ax = plt.subplots(figsize=(6, 5))
        n_nodes = 60
        cx, cy = 250, 200
        r_layout = 150
        
        nodes_coords = []
        for i in range(n_nodes):
            angle = (i / n_nodes) * 2 * np.pi
            x = cx + r_layout * np.cos(angle)
            y = cy + r_layout * np.sin(angle)
            nodes_coords.append((x, y))
            
        # Draw ring connections
        for i, coord in enumerate(nodes_coords):
            next_coord = nodes_coords[(i + 1) % n_nodes]
            ax.plot([coord[0], next_coord[0]], [coord[1], next_coord[1]], color='#CBD5E1', linewidth=0.7)
            
            # Small world shortcut links
            if i % 8 == 0:
                target_coord = nodes_coords[(i + 15) % n_nodes]
                ax.plot([coord[0], target_coord[0]], [coord[1], target_coord[1]], color='#2563EB', linewidth=1.2, alpha=0.7)
                
        # Draw node circles
        for i, coord in enumerate(nodes_coords):
            is_local = i == 1
            color = '#2563EB' if is_local else '#0D9488'
            size = 90 if is_local else 30
            ax.scatter(coord[0], coord[1], color=color, s=size, zorder=3)
            
        ax.set_xlim(50, 450)
        ax.set_ylim(0, 400)
        ax.axis('off')
        st.pyplot(fig)

    with col2:
        st.subheader("Consensus Error Progression")
        if not st.session_state.fl_consensus_history:
            st.info("Click 'Advance Decentralized Gossip Round' to generate the consensus convergence curve.")
        else:
            setup_matplotlib_clinical_theme()
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(range(1, st.session_state.fl_round + 1), st.session_state.fl_consensus_history, marker='o', color='#2563EB', linewidth=2.0)
            ax.set_xlabel("Communication Round")
            ax.set_ylabel("Consensus Disagreement Error")
            st.pyplot(fig)

    render_disclaimer()
