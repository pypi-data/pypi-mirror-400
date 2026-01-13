"""
NanoPy Bank - Streamlit UI with shadcn components
"""

import streamlit as st
from streamlit_option_menu import option_menu

try:
    from .core import get_bank
    from .core.auth import get_auth_service, UserRole
    from .ui.pages import (
        render_dashboard, render_accounts, render_transfers,
        render_beneficiaries, render_cards, render_loans,
        render_fees, render_branches, render_sepa,
        render_audit, render_settings, render_advisor, render_holding
    )
    from .ui.pages.login import render_login
except ImportError:
    from nanopy_bank.core import get_bank
    from nanopy_bank.core.auth import get_auth_service, UserRole
    from nanopy_bank.ui.pages import (
        render_dashboard, render_accounts, render_transfers,
        render_beneficiaries, render_cards, render_loans,
        render_fees, render_branches, render_sepa,
        render_audit, render_settings, render_advisor, render_holding
    )
    from nanopy_bank.ui.pages.login import render_login


# Page config
st.set_page_config(
    page_title="NanoPy Bank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #00d4ff, #7b2cbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .user-badge {
        background: linear-gradient(135deg, #1e3a5f, #2d1b4e);
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state"""
    if "bank" not in st.session_state:
        st.session_state.bank = get_bank()
    if "current_account" not in st.session_state:
        st.session_state.current_account = None
    if "current_customer" not in st.session_state:
        st.session_state.current_customer = None
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "session_id" not in st.session_state:
        st.session_state.session_id = None


def logout():
    """Logout user"""
    if st.session_state.session_id:
        auth = get_auth_service()
        auth.logout(st.session_state.session_id)
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.session_id = None
    st.rerun()


def get_role_label(role: UserRole) -> str:
    """Get French label for role"""
    labels = {
        UserRole.CLIENT: "Client",
        UserRole.ADVISOR: "Conseiller",
        UserRole.DIRECTOR: "Directeur",
        UserRole.ADMIN: "Administrateur",
        UserRole.HOLDING: "Holding",
    }
    return labels.get(role, "Utilisateur")


def get_role_color(role: UserRole) -> str:
    """Get color for role"""
    colors = {
        UserRole.CLIENT: "#00d4ff",
        UserRole.ADVISOR: "#7b2cbf",
        UserRole.DIRECTOR: "#ff6b6b",
        UserRole.ADMIN: "#ffd93d",
        UserRole.HOLDING: "#00ff88",
    }
    return colors.get(role, "#888888")


def render_sidebar():
    """Render sidebar navigation based on user role"""
    user = st.session_state.user
    role = user.role if user else UserRole.CLIENT

    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2">
                <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                <line x1="1" y1="10" x2="23" y2="10"></line>
            </svg>
            <span style="font-size: 1.5rem; font-weight: bold; background: linear-gradient(90deg, #00d4ff, #7b2cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">NanoPy Bank</span>
        </div>
        """, unsafe_allow_html=True)

        # User info
        role_color = get_role_color(role)
        st.markdown(f"""
        <div class="user-badge">
            <div style="font-size: 14px; font-weight: bold; color: white;">{user.display_name}</div>
            <div style="font-size: 12px; color: {role_color};">{get_role_label(role)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Logout button
        if st.button("Deconnexion", use_container_width=True):
            logout()

        st.divider()

        page = None
        page2 = None
        page3 = None

        # Holding user - only sees Group menu
        if role == UserRole.HOLDING:
            st.markdown("##### Espace Groupe")
            page3 = option_menu(
                menu_title=None,
                options=["Tableau de bord", "Tresorerie", "Investissements", "Assurances", "Filiales", "Consolidation", "Risques", "Gouvernance"],
                icons=["speedometer2", "bank", "graph-up-arrow", "shield", "building", "bar-chart", "shield-exclamation", "people"],
                default_index=0,
                key="menu3",
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#00ff88", "font-size": "16px"},
                    "nav-link": {"font-size": "13px", "text-align": "left", "margin": "2px 0", "padding": "8px 10px", "--hover-color": "#1e1e2f", "border-radius": "6px"},
                    "nav-link-selected": {"background-color": "#1b4e2d", "color": "#00ff88"},
                }
            )
        else:
            # Client menu - visible to CLIENT, ADVISOR, DIRECTOR, ADMIN
            st.markdown("##### Espace Client")
            page = option_menu(
                menu_title=None,
                options=["Dashboard", "Comptes", "Virements", "Beneficiaires", "Cartes", "Credits", "Frais", "SEPA"],
                icons=["speedometer2", "wallet2", "arrow-left-right", "people", "credit-card", "cash-stack", "percent", "file-earmark-code"],
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#00d4ff", "font-size": "16px"},
                    "nav-link": {"font-size": "13px", "text-align": "left", "margin": "2px 0", "padding": "8px 10px", "--hover-color": "#1e1e2f", "border-radius": "6px"},
                    "nav-link-selected": {"background-color": "#1e3a5f", "color": "#00d4ff"},
                }
            )

            # Bank menu - visible to ADVISOR and above (but not HOLDING)
            if user.can_access(UserRole.ADVISOR) and role != UserRole.HOLDING:
                st.divider()
                st.markdown("##### Espace Banque")

                bank_options = ["Conseiller"]
                bank_icons = ["person-badge"]

                if user.can_access(UserRole.DIRECTOR):
                    bank_options.extend(["Agences", "Audit"])
                    bank_icons.extend(["building", "shield-check"])

                if user.can_access(UserRole.ADMIN):
                    bank_options.append("Administration")
                    bank_icons.append("gear")

                page2 = option_menu(
                    menu_title=None,
                    options=bank_options,
                    icons=bank_icons,
                    default_index=0,
                    key="menu2",
                    styles={
                        "container": {"padding": "0!important", "background-color": "transparent"},
                        "icon": {"color": "#7b2cbf", "font-size": "16px"},
                        "nav-link": {"font-size": "13px", "text-align": "left", "margin": "2px 0", "padding": "8px 10px", "--hover-color": "#1e1e2f", "border-radius": "6px"},
                        "nav-link-selected": {"background-color": "#2d1b4e", "color": "#7b2cbf"},
                    }
                )

        st.divider()

        # Quick stats
        bank = st.session_state.bank
        stats = bank.get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Comptes", stats["total_accounts"])
        with col2:
            st.metric("Transactions", stats["total_transactions"])

        return page, page2, page3


def main():
    """Main app entry point"""
    init_session_state()

    # Check if logged in
    if not st.session_state.logged_in:
        render_login()
        return

    page, page2, page3 = render_sidebar()
    user = st.session_state.user

    # Map French menu to render functions
    client_pages = {
        "Dashboard": render_dashboard,
        "Comptes": render_accounts,
        "Virements": render_transfers,
        "Beneficiaires": render_beneficiaries,
        "Cartes": render_cards,
        "Credits": render_loans,
        "Frais": render_fees,
        "SEPA": render_sepa,
    }

    bank_pages = {
        "Conseiller": render_advisor,
        "Agences": render_branches,
        "Audit": render_audit,
        "Administration": render_settings,
    }

    # Holding has separate pages per tab
    group_pages = {
        "Tableau de bord": "dashboard",
        "Tresorerie": "tresorerie",
        "Investissements": "investissements",
        "Assurances": "assurances",
        "Filiales": "filiales",
        "Consolidation": "consolidation",
        "Risques": "risques",
        "Gouvernance": "gouvernance",
    }

    # Determine active page from menus
    active_page = None
    if page3 and page3 in group_pages:
        # Holding user - render holding page with selected tab
        render_holding(tab=group_pages[page3])
    elif page2 and page2 in bank_pages:
        active_page = page2
        bank_pages[active_page]()
    elif page and page in client_pages:
        active_page = page
        client_pages[active_page]()


if __name__ == "__main__":
    main()
