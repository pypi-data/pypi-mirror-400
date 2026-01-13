"""
Dashboard page
"""

import streamlit as st
import streamlit_shadcn_ui as ui
from decimal import Decimal

from .common import format_currency, page_header


def render_dashboard():
    """Render dashboard page"""
    page_header("Dashboard")

    bank = st.session_state.bank

    if bank.accounts:
        accounts = list(bank.accounts.values())
        account_options = {f"{acc.account_name} ({acc.format_iban()})": acc.iban for acc in accounts}

        selected = st.selectbox("Select Account", options=list(account_options.keys()), key="account_selector")

        if selected:
            iban = account_options[selected]
            account = bank.get_account(iban)
            st.session_state.current_account = account

            col1, col2, col3 = st.columns(3)

            with col1:
                ui.metric_card(
                    title="Current Balance",
                    content=format_currency(account.balance, account.currency.value),
                    description=f"Available: {format_currency(account.available_balance, account.currency.value)}",
                    key="balance_card"
                )

            with col2:
                ui.metric_card(
                    title="Account Type",
                    content=account.account_type.value.title(),
                    description=f"Status: {account.status.value.title()}",
                    key="type_card"
                )

            with col3:
                ui.metric_card(
                    title="IBAN",
                    content=account.format_iban()[:19] + "...",
                    description=f"BIC: {account.bic}",
                    key="iban_card"
                )

            st.divider()

            st.markdown("### Recent Transactions")
            transactions = bank.get_account_transactions(iban, limit=10)

            if transactions:
                for tx in transactions:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    with col1:
                        st.markdown(f"**{tx.label}**")
                        st.caption(tx.counterparty_name or tx.description)
                    with col2:
                        st.caption(tx.created_at.strftime("%d/%m/%Y %H:%M"))
                    with col3:
                        color = "green" if tx.is_credit else "red"
                        sign = "+" if tx.is_credit else "-"
                        st.markdown(f":{color}[{sign}{format_currency(tx.amount, tx.currency.value)}]")
                    with col4:
                        st.caption(tx.transaction_type.value)
                    st.divider()
            else:
                st.info("No transactions yet")

    else:
        st.warning("No accounts found. Create one in the Accounts section.")

        if ui.button("Create Demo Account", key="create_demo"):
            from nanopy_bank.core import AccountType, TransactionType

            customer = bank.create_customer(
                first_name="John", last_name="Doe",
                email="john.doe@example.com", phone="+33612345678",
                address="123 Rue de la Paix", city="Paris",
                postal_code="75001", country="FR"
            )
            account = bank.create_account(
                customer_id=customer.customer_id,
                account_type=AccountType.CHECKING,
                initial_balance=Decimal("1500.00"),
                account_name="Compte Principal"
            )
            bank.credit(account.iban, Decimal("2500.00"), "Salaire Janvier", "ACME Corp", "", TransactionType.SEPA_CREDIT)
            bank.debit(account.iban, Decimal("45.90"), "Carrefour", "CARREFOUR", "", TransactionType.CARD_PAYMENT, category="Courses")

            st.success(f"Demo account created: {account.format_iban()}")
            st.rerun()
