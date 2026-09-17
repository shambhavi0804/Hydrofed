"""
Administrator Management View for HydroFed-ICAF.
"""

import pandas as pd
import streamlit as st
from database.schema import get_db_connection
from frontend.components import render_header, render_disclaimer

def render_admin_view(create_user_func):
    render_header(
        "Hospital User & Administrator Management",
        "Manage authorized hospital clinician logins and system security roles."
    )

    if st.session_state.get("user_role") != "admin":
        st.error("Administrator access privileges required to view this section.")
        render_disclaimer()
        return

    st.subheader("Create New Clinician / Administrator Account")
    with st.form("create_admin_account_form"):
        new_username = st.text_input("New Username *")
        new_role = st.selectbox("Assigned Role", ["clinician", "admin"])
        new_password = st.text_input("Temporary Password *", type="password")
        new_confirm = st.text_input("Confirm Password *", type="password")
        create = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        if create:
            if not new_username.strip() or len(new_password) < 8:
                st.error("Username is required and password must contain at least 8 characters.")
            elif new_password != new_confirm:
                st.error("Passwords do not match.")
            else:
                ok, msg = create_user_func(new_username.strip(), new_password, new_role)
                if ok:
                    st.success(f"Account for '{new_username.strip()}' created successfully.")
                else:
                    st.error(f"Unable to create account: {msg}")

    conn = get_db_connection()
    users = conn.execute("SELECT username, role, active, created_at FROM app_users ORDER BY created_at DESC").fetchall()
    conn.close()

    st.subheader("Registered Hospital Personnel Accounts")
    st.dataframe(pd.DataFrame(users, columns=["Username", "Role", "Active", "Created"]), use_container_width=True, hide_index=True)

    render_disclaimer()
