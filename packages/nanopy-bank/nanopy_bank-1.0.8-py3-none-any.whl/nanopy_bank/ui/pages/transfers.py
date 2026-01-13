"""
Transfers page
"""

import streamlit as st
from decimal import Decimal

from .common import format_currency, page_header


def render_transfers():
    """Render transfers page"""
    page_header("Transfers")

    bank = st.session_state.bank

    if not bank.accounts:
        st.warning("No accounts available. Create one first.")
        return

    tab1, tab2 = st.tabs(["New Transfer", "Transfer History"])

    with tab1:
        st.markdown("### New Transfer")

        with st.form("transfer_form"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**From Account**")
                from_options = {f"{acc.account_name} ({format_currency(acc.balance)})": acc.iban for acc in bank.accounts.values()}
                from_account = st.selectbox("Source Account", options=list(from_options.keys()))

                st.markdown("**Amount**")
                amount = st.number_input("Amount (EUR)", min_value=0.01, value=100.0, step=10.0)

            with col2:
                st.markdown("**To Account**")
                transfer_type = st.radio("Transfer Type", ["Internal", "External (SEPA)"])

                if transfer_type == "Internal":
                    to_options = {f"{acc.account_name}": acc.iban for acc in bank.accounts.values()}
                    to_account = st.selectbox("Destination Account", options=list(to_options.keys()))
                    to_iban = to_options[to_account]
                    to_name = ""
                    to_bic = ""
                else:
                    to_iban = st.text_input("Beneficiary IBAN", placeholder="FR76 1234 5678 9012 3456 7890 123")
                    to_bic = st.text_input("BIC (optional)", placeholder="BNPAFRPP")
                    to_name = st.text_input("Beneficiary Name")

            label = st.text_input("Label/Reference", placeholder="Rent payment")

            submitted = st.form_submit_button("Send Transfer", type="primary")

            if submitted:
                try:
                    from_iban = from_options[from_account]

                    if transfer_type == "Internal":
                        debit_tx, credit_tx = bank.transfer(from_iban, to_iban, Decimal(str(amount)), label)
                        st.success(f"Transfer completed! Reference: {debit_tx.reference}")
                    else:
                        tx = bank.sepa_credit_transfer(from_iban, to_iban, to_bic, to_name, Decimal(str(amount)), label)
                        st.success(f"SEPA transfer initiated! Reference: {tx.reference}")

                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab2:
        st.markdown("### Recent Transfers")

        from nanopy_bank.core import TransactionType

        all_transfers = [
            tx for tx in bank.transactions.values()
            if tx.transaction_type in [TransactionType.TRANSFER, TransactionType.SEPA_CREDIT]
        ]
        all_transfers.sort(key=lambda x: x.created_at, reverse=True)

        if all_transfers:
            for tx in all_transfers[:20]:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.markdown(f"**{tx.label}**")
                    st.caption(f"{tx.from_iban or 'N/A'} → {tx.to_iban or tx.counterparty_iban or 'N/A'}")
                with col2:
                    st.caption(tx.created_at.strftime("%d/%m/%Y %H:%M"))
                with col3:
                    st.markdown(f":red[-{format_currency(tx.amount)}]")
                st.divider()
        else:
            st.info("No transfers yet")
