"""
Accounts page
"""

import streamlit as st
from decimal import Decimal

from .common import format_currency, page_header


def render_accounts():
    """Render accounts page"""
    page_header("Accounts")

    bank = st.session_state.bank

    if bank.accounts:
        st.markdown("### Your Accounts")

        for iban, account in bank.accounts.items():
            with st.expander(f"💳 {account.account_name} - {account.format_iban()}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Balance:** {format_currency(account.balance, account.currency.value)}")
                    st.markdown(f"**Available:** {format_currency(account.available_balance, account.currency.value)}")
                    st.markdown(f"**Type:** {account.account_type.value.title()}")
                with col2:
                    st.markdown(f"**IBAN:** `{account.format_iban()}`")
                    st.markdown(f"**BIC:** `{account.bic}`")
                    st.markdown(f"**Status:** {account.status.value.title()}")

    st.divider()

    st.markdown("### Create New Account")

    with st.form("create_account_form"):
        col1, col2 = st.columns(2)

        with col1:
            if bank.customers:
                customer_options = {f"{c.full_name} ({c.customer_id})": c.customer_id for c in bank.customers.values()}
                customer_select = st.selectbox("Select Customer", options=["New Customer"] + list(customer_options.keys()))
            else:
                customer_select = "New Customer"

            if customer_select == "New Customer":
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email = st.text_input("Email")
            else:
                first_name = last_name = email = None
                selected_customer_id = customer_options[customer_select]

        with col2:
            from nanopy_bank.core import AccountType, Currency

            account_name = st.text_input("Account Name", "Mon Compte")
            account_type = st.selectbox("Account Type", [at.value for at in AccountType])
            currency = st.selectbox("Currency", [c.value for c in Currency])
            initial_balance = st.number_input("Initial Balance", min_value=0.0, value=0.0, step=100.0)

        submitted = st.form_submit_button("Create Account")

        if submitted:
            try:
                if customer_select == "New Customer":
                    if not first_name or not last_name or not email:
                        st.error("Please fill in all customer fields")
                    else:
                        customer = bank.create_customer(first_name, last_name, email)
                        selected_customer_id = customer.customer_id
                else:
                    selected_customer_id = customer_options[customer_select]

                account = bank.create_account(
                    customer_id=selected_customer_id,
                    account_type=AccountType(account_type),
                    currency=Currency(currency),
                    initial_balance=Decimal(str(initial_balance)),
                    account_name=account_name
                )
                st.success(f"Account created: {account.format_iban()}")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
