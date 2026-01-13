"""
Settings page
"""

import streamlit as st

from .common import page_header


def render_settings():
    """Render settings page"""
    page_header("Settings")

    bank = st.session_state.bank

    st.markdown("### Bank Information")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Bank Name", value="NanoPy Bank", disabled=True)
        st.text_input("BIC", value="NANPFRPP", disabled=True)
    with col2:
        st.text_input("Country", value="France", disabled=True)
        st.text_input("Data Directory", value=str(bank.data_dir), disabled=True)

    st.divider()

    st.markdown("### Customers")
    if bank.customers:
        for cust_id, customer in bank.customers.items():
            with st.expander(f"👤 {customer.full_name} ({cust_id})"):
                st.markdown(f"**Email:** {customer.email}")
                st.markdown(f"**Phone:** {customer.phone}")
                st.markdown(f"**Address:** {customer.address}, {customer.postal_code} {customer.city}")
                st.markdown(f"**Created:** {customer.created_at.strftime('%d/%m/%Y')}")

    st.divider()

    st.markdown("### Danger Zone")
    if st.button("Reset All Data", type="secondary"):
        if st.checkbox("I confirm I want to delete all data"):
            import shutil
            shutil.rmtree(bank.data_dir, ignore_errors=True)
            bank.data_dir.mkdir(parents=True, exist_ok=True)
            bank.customers.clear()
            bank.accounts.clear()
            bank.transactions.clear()
            st.success("All data has been reset")
            st.rerun()
