"""
Clinical Design System and CSS Injection for HydroFed-ICAF Streamlit Application.
Provides institutional medical styling, readable cards, status badges, and typography.
"""

import streamlit as st

def inject_clinical_css():
    """Injects high-grade clinical CSS styling into the Streamlit app."""
    st.markdown("""
    <style>
        /* ==========================================================================
           1. ROOT PALETTE & GLOBAL TYPOGRAPHY
           ========================================================================== */
        :root {
            --color-primary-navy: #173B65;
            --color-secondary-blue: #2563EB;
            --color-accent-teal: #0D9488;
            --color-text-main: #1E293B;
            --color-text-muted: #64748B;
            --color-bg-light: #F8FAFC;
            --color-card-bg: #FFFFFF;
            --color-border: #E2E8F0;
            --color-border-dark: #CBD5E1;
            
            --color-danger: #DC2626;
            --color-danger-bg: #FEE2E2;
            --color-success: #16A34A;
            --color-success-bg: #DCFCE7;
            --color-warning: #D97706;
            --color-warning-bg: #FEF3C7;
            --color-info: #0284C7;
            --color-info-bg: #E0F2FE;
        }

        /* App Background & Base Text */
        .stApp {
            background-color: var(--color-bg-light) !important;
            color: var(--color-text-main) !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid var(--color-border) !important;
        }
        section[data-testid="stSidebar"] * {
            color: var(--color-text-main) !important;
        }

        /* Clean Headers */
        h1 {
            color: var(--color-primary-navy) !important;
            font-weight: 700 !important;
            font-size: 1.65rem !important;
            letter-spacing: -0.02em !important;
            margin-bottom: 0.35rem !important;
            padding-bottom: 0.2rem !important;
            border-bottom: 1px solid var(--color-border) !important;
        }
        h2 {
            color: var(--color-primary-navy) !important;
            font-weight: 600 !important;
            font-size: 1.35rem !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        h3 {
            color: var(--color-primary-navy) !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            margin-top: 0.75rem !important;
            margin-bottom: 0.35rem !important;
        }
        h4, h5, h6 {
            color: var(--color-text-main) !important;
            font-weight: 600 !important;
        }

        /* ==========================================================================
           2. CLINICAL CARD & METRIC CONTAINERS
           ========================================================================== */
        .metric-card {
            background: var(--color-card-bg) !important;
            border: 1px solid var(--color-border) !important;
            border-radius: 10px !important;
            padding: 16px 18px !important;
            margin-bottom: 14px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
            transition: all 0.2s ease-in-out !important;
        }
        .metric-card:hover {
            border-color: var(--color-border-dark) !important;
            box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.06), 0 2px 4px -2px rgba(0, 0, 0, 0.04) !important;
        }

        .metric-card-primary {
            border-left: 4px solid var(--color-secondary-blue) !important;
        }
        .metric-card-danger {
            border-left: 4px solid var(--color-danger) !important;
            background: linear-gradient(180deg, #FFFFFF 0%, var(--color-danger-bg) 100%) !important;
        }
        .metric-card-success {
            border-left: 4px solid var(--color-success) !important;
            background: linear-gradient(180deg, #FFFFFF 0%, var(--color-success-bg) 100%) !important;
        }
        .metric-card-warning {
            border-left: 4px solid var(--color-warning) !important;
            background: linear-gradient(180deg, #FFFFFF 0%, var(--color-warning-bg) 100%) !important;
        }

        /* Subtitle & Muted Label */
        .card-label {
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
            color: var(--color-text-muted) !important;
            margin-bottom: 4px !important;
            display: block !important;
        }
        .card-value {
            font-size: 1.45rem !important;
            font-weight: 700 !important;
            color: var(--color-primary-navy) !important;
            line-height: 1.2 !important;
        }

        /* ==========================================================================
           3. CLINICAL STATUS BADGES
           ========================================================================== */
        .badge {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 4px 12px !important;
            border-radius: 6px !important;
            font-size: 0.82rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.03em !important;
            line-height: 1.3 !important;
            text-transform: uppercase !important;
        }
        .badge-danger {
            background-color: var(--color-danger-bg) !important;
            color: var(--color-danger) !important;
            border: 1px solid #FCA5A5 !important;
        }
        .badge-success {
            background-color: var(--color-success-bg) !important;
            color: var(--color-success) !important;
            border: 1px solid #86EFAC !important;
        }
        .badge-warning {
            background-color: var(--color-warning-bg) !important;
            color: var(--color-warning) !important;
            border: 1px solid #FCD34D !important;
        }
        .badge-primary {
            background-color: var(--color-info-bg) !important;
            color: var(--color-secondary-blue) !important;
            border: 1px solid #93C5FD !important;
        }

        /* ==========================================================================
           4. CLINICAL CALLOUTS & BANNERS
           ========================================================================== */
        .clinical-banner {
            border-radius: 8px !important;
            padding: 12px 16px !important;
            margin: 10px 0 16px 0 !important;
            font-size: 0.88rem !important;
            line-height: 1.45 !important;
        }
        .clinical-banner-info {
            background-color: var(--color-info-bg) !important;
            border: 1px solid #BAE6FD !important;
            color: #0369A1 !important;
        }
        .clinical-banner-warning {
            background-color: var(--color-warning-bg) !important;
            border: 1px solid #FDE68A !important;
            color: #92400E !important;
        }
        .clinical-banner-danger {
            background-color: var(--color-danger-bg) !important;
            border: 1px solid #FECACA !important;
            color: #991B1B !important;
        }
        .clinical-banner-success {
            background-color: var(--color-success-bg) !important;
            border: 1px solid #BBF7D0 !important;
            color: #166534 !important;
        }

        /* Disclaimer Footer Callout */
        .disclaimer-card {
            background-color: #F8FAFC !important;
            border: 1px solid #CBD5E1 !important;
            border-left: 4px solid var(--color-primary-navy) !important;
            border-radius: 6px !important;
            padding: 10px 14px !important;
            margin-top: 20px !important;
            font-size: 0.78rem !important;
            color: #475569 !important;
            line-height: 1.4 !important;
        }

        /* ==========================================================================
           5. FORM CONTROLS & BUTTONS
           ========================================================================== */
        .stButton > button {
            border-radius: 6px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 6px 16px !important;
            transition: all 0.15s ease-in-out !important;
        }
        .stButton > button:hover {
            border-color: var(--color-secondary-blue) !important;
            color: var(--color-secondary-blue) !important;
        }

        /* DataTables and Tabbed UI */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--color-border) !important;
            border-radius: 8px !important;
            background: #FFFFFF !important;
        }
    </style>
    """, unsafe_allow_html=True)
