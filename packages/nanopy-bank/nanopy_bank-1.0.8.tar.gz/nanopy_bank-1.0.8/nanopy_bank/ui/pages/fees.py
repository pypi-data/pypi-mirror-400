"""
Fees page
"""

import streamlit as st
import pandas as pd

from .common import page_header


def render_fees():
    """Render fees and rates page"""
    page_header("Fees & Rates")

    tab1, tab2 = st.tabs(["Banking Fees", "Interest Rates"])

    with tab1:
        st.markdown("### Banking Fees Schedule")

        fees = [
            {"name": "Account Maintenance", "amount": "2.00 EUR", "frequency": "Monthly"},
            {"name": "Visa Card Annual Fee", "amount": "45.00 EUR", "frequency": "Yearly"},
            {"name": "SEPA Transfer", "amount": "Free", "frequency": "Per transaction"},
            {"name": "International Transfer", "amount": "15.00 EUR", "frequency": "Per transaction"},
            {"name": "Overdraft Fee", "amount": "8.00 EUR", "frequency": "Per occurrence"},
            {"name": "Rejected Payment", "amount": "20.00 EUR", "frequency": "Per occurrence"},
            {"name": "ATM (Other Banks)", "amount": "1.00 EUR", "frequency": "After 3/month"},
            {"name": "Currency Conversion", "amount": "2.00%", "frequency": "Per transaction"},
        ]

        df = pd.DataFrame(fees)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### Current Interest Rates")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Savings Rates")
            savings_rates = [
                {"product": "Livret A", "rate": "3.00%"},
                {"product": "LDDS", "rate": "3.00%"},
                {"product": "LEP", "rate": "5.00%"},
                {"product": "PEL", "rate": "2.00%"},
            ]
            for r in savings_rates:
                st.markdown(f"**{r['product']}**: :green[{r['rate']}]")

        with col2:
            st.markdown("#### Loan Rates")
            loan_rates = [
                {"product": "Personal Loan", "rate": "5.50%"},
                {"product": "Auto Loan", "rate": "4.90%"},
                {"product": "Mortgage (20yr)", "rate": "3.80%"},
                {"product": "Overdraft (Authorized)", "rate": "7.00%"},
                {"product": "Overdraft (Unauthorized)", "rate": "16.00%"},
            ]
            for r in loan_rates:
                st.markdown(f"**{r['product']}**: :red[{r['rate']}]")
