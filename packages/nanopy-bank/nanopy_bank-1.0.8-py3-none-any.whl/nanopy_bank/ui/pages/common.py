"""
Common utilities for UI pages
"""

import streamlit as st
from decimal import Decimal


def format_currency(amount: Decimal, currency: str = "EUR") -> str:
    """Format amount with currency symbol"""
    symbols = {"EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF"}
    symbol = symbols.get(currency, currency)
    return f"{amount:,.2f} {symbol}"


def page_header(title: str):
    """Render page header"""
    st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
