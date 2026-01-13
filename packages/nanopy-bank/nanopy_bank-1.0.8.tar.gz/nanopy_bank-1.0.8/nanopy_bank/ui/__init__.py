"""
UI Module - Streamlit application
"""

from .pages import dashboard, accounts, transfers, cards, sepa, settings

__all__ = [
    "dashboard",
    "accounts",
    "transfers",
    "cards",
    "sepa",
    "settings",
]
