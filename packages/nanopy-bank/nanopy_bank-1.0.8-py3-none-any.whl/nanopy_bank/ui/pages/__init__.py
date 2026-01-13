"""
UI Pages - Each page in its own module
"""

from .dashboard import render_dashboard
from .accounts import render_accounts
from .transfers import render_transfers
from .beneficiaries import render_beneficiaries
from .cards import render_cards
from .loans import render_loans
from .fees import render_fees
from .branches import render_branches
from .sepa import render_sepa
from .audit import render_audit
from .settings import render_settings
from .advisor import render_advisor
from .holding import render_holding

__all__ = [
    "render_dashboard",
    "render_accounts",
    "render_transfers",
    "render_beneficiaries",
    "render_cards",
    "render_loans",
    "render_fees",
    "render_branches",
    "render_sepa",
    "render_audit",
    "render_settings",
    "render_advisor",
    "render_holding",
]
