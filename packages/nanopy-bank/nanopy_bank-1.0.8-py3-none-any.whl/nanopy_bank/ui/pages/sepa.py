"""
SEPA page
"""

import streamlit as st
from datetime import datetime, timedelta
from decimal import Decimal

from .common import page_header


def render_sepa():
    """Render SEPA XML page"""
    page_header("SEPA XML")

    bank = st.session_state.bank

    tab1, tab2, tab3 = st.tabs(["Export Statement", "Export Credit Transfer", "Import XML"])

    with tab1:
        st.markdown("### Export Bank Statement (camt.053)")

        if bank.accounts:
            account_options = {f"{acc.account_name} ({acc.format_iban()})": acc.iban for acc in bank.accounts.values()}
            selected = st.selectbox("Select Account", options=list(account_options.keys()), key="stmt_account")

            col1, col2 = st.columns(2)
            with col1:
                from_date = st.date_input("From Date", value=datetime.now() - timedelta(days=30))
            with col2:
                to_date = st.date_input("To Date", value=datetime.now())

            if st.button("Generate Statement XML", key="gen_stmt"):
                from nanopy_bank.sepa import SEPAGenerator

                iban = account_options[selected]
                account = bank.get_account(iban)
                transactions = bank.get_account_transactions(iban, limit=100)

                generator = SEPAGenerator(
                    initiator_name="NanoPy Bank",
                    initiator_iban=iban,
                    initiator_bic=account.bic
                )

                xml_content = generator.generate_statement(
                    iban=iban,
                    transactions=transactions,
                    opening_balance=account.balance - sum(tx.signed_amount for tx in transactions),
                    closing_balance=account.balance,
                    from_date=datetime.combine(from_date, datetime.min.time()),
                    to_date=datetime.combine(to_date, datetime.max.time())
                )

                st.download_button(
                    label="Download camt.053.xml",
                    data=xml_content,
                    file_name=f"statement_{iban}_{to_date.strftime('%Y%m%d')}.xml",
                    mime="application/xml"
                )

                with st.expander("Preview XML"):
                    st.code(xml_content, language="xml")

    with tab2:
        st.markdown("### Export Credit Transfer (pain.001)")
        st.info("Create a SEPA batch payment file")

        with st.form("sepa_export_form"):
            if bank.accounts:
                account_options = {f"{acc.account_name}": acc.iban for acc in bank.accounts.values()}
                from_account = st.selectbox("From Account", options=list(account_options.keys()))

            to_name = st.text_input("Beneficiary Name")
            to_iban = st.text_input("Beneficiary IBAN")
            to_bic = st.text_input("Beneficiary BIC")
            amount = st.number_input("Amount", min_value=0.01, value=100.0)
            reference = st.text_input("Reference/Label")

            if st.form_submit_button("Generate XML"):
                from nanopy_bank.sepa import SEPAGenerator

                from_iban = account_options[from_account]
                account = bank.get_account(from_iban)

                generator = SEPAGenerator(
                    initiator_name="NanoPy Bank Client",
                    initiator_iban=from_iban,
                    initiator_bic=account.bic
                )

                xml_content = generator.generate_credit_transfer([{
                    "amount": Decimal(str(amount)),
                    "creditor_name": to_name,
                    "creditor_iban": to_iban,
                    "creditor_bic": to_bic,
                    "remittance_info": reference
                }])

                st.download_button(
                    label="Download pain.001.xml",
                    data=xml_content,
                    file_name=f"sepa_transfer_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml",
                    mime="application/xml"
                )

                with st.expander("Preview XML"):
                    st.code(xml_content, language="xml")

    with tab3:
        st.markdown("### Import SEPA XML")

        uploaded_file = st.file_uploader("Upload XML file", type=["xml"])

        if uploaded_file:
            content = uploaded_file.read().decode()
            st.code(content[:2000] + "..." if len(content) > 2000 else content, language="xml")
            st.info("XML parsing available. Transactions can be imported.")
