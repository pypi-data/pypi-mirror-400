"""
Beneficiaries page
"""

import streamlit as st

from .common import page_header


def render_beneficiaries():
    """Render beneficiaries page"""
    page_header("Beneficiaries")

    bank = st.session_state.bank

    tab1, tab2, tab3 = st.tabs(["Saved Beneficiaries", "Standing Orders", "SEPA Mandates"])

    with tab1:
        st.markdown("### Saved Beneficiaries")

        with st.expander("Add New Beneficiary", expanded=False):
            with st.form("add_beneficiary"):
                col1, col2 = st.columns(2)
                with col1:
                    ben_name = st.text_input("Beneficiary Name")
                    ben_iban = st.text_input("IBAN")
                    ben_bic = st.text_input("BIC (optional)")
                with col2:
                    ben_alias = st.text_input("Alias (e.g., 'Mom', 'Landlord')")
                    ben_category = st.selectbox("Category", ["family", "bills", "business", "friends", "other"])

                if st.form_submit_button("Add Beneficiary"):
                    st.success(f"Beneficiary '{ben_name}' added!")

        demo_beneficiaries = [
            {"name": "Marie Dupont", "iban": "FR76 1441 0000 0112 3456 7890 123", "alias": "Maman", "category": "family"},
            {"name": "SCI Les Lilas", "iban": "FR76 3000 4000 0312 3456 7890 143", "alias": "Proprietaire", "category": "bills"},
            {"name": "EDF", "iban": "FR76 3000 1007 9412 3456 7890 185", "alias": "Electricite", "category": "bills"},
        ]

        for ben in demo_beneficiaries:
            col1, col2, col3, col4 = st.columns([3, 3, 2, 1])
            with col1:
                st.markdown(f"**{ben['name']}**")
                st.caption(ben['alias'])
            with col2:
                st.code(ben['iban'], language=None)
            with col3:
                st.caption(ben['category'])
            with col4:
                st.button("Use", key=f"use_{ben['iban']}")
            st.divider()

    with tab2:
        st.markdown("### Standing Orders (Virements Permanents)")

        with st.expander("Create Standing Order", expanded=False):
            with st.form("add_standing_order"):
                col1, col2 = st.columns(2)
                with col1:
                    if bank.accounts:
                        from_options = {acc.account_name: acc.iban for acc in bank.accounts.values()}
                        st.selectbox("From Account", list(from_options.keys()))
                    st.text_input("To IBAN")
                    st.text_input("Beneficiary Name")
                with col2:
                    st.number_input("Amount (EUR)", min_value=0.01, value=100.0)
                    st.selectbox("Frequency", ["Monthly", "Weekly", "Quarterly", "Yearly"])
                    st.number_input("Execution Day", min_value=1, max_value=28, value=1)
                st.text_input("Label")

                if st.form_submit_button("Create Standing Order"):
                    st.success("Standing order created!")

        demo_orders = [
            {"label": "Loyer mensuel", "to": "SCI Les Lilas", "amount": "850.00", "frequency": "Monthly", "next": "05/02/2026"},
            {"label": "Epargne mensuelle", "to": "Mon Livret A", "amount": "200.00", "frequency": "Monthly", "next": "01/02/2026"},
        ]

        for order in demo_orders:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.markdown(f"**{order['label']}**")
                st.caption(f"To: {order['to']}")
            with col2:
                st.markdown(f":blue[{order['amount']} EUR]")
                st.caption(order['frequency'])
            with col3:
                st.caption(f"Next: {order['next']}")
            with col4:
                st.button("Edit", key=f"edit_order_{order['label']}")
            st.divider()

    with tab3:
        st.markdown("### SEPA Mandates (Mandats de Prelevement)")
        st.info("Manage your direct debit authorizations here.")

        demo_mandates = [
            {"creditor": "Netflix", "reference": "MNDT-NF-001234", "max": "19.99", "status": "Active"},
            {"creditor": "EDF", "reference": "MNDT-EDF-005678", "max": "200.00", "status": "Active"},
            {"creditor": "Orange", "reference": "MNDT-OR-009012", "max": "50.00", "status": "Active"},
        ]

        for mandate in demo_mandates:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.markdown(f"**{mandate['creditor']}**")
                st.caption(mandate['reference'])
            with col2:
                st.markdown(f"Max: {mandate['max']} EUR")
            with col3:
                st.success(mandate['status'])
            with col4:
                st.button("Revoke", key=f"revoke_{mandate['reference']}")
            st.divider()
