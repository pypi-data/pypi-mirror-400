"""
Audit page
"""

import streamlit as st

from .common import page_header


def render_audit():
    """Render audit logs page"""
    page_header("Security & Audit")

    tab1, tab2 = st.tabs(["Activity Log", "Security Alerts"])

    with tab1:
        st.markdown("### Recent Activity")

        logs = [
            {"time": "05/01/2026 14:32", "action": "Login", "details": "Successful login from Paris, FR", "ip": "86.123.45.67"},
            {"time": "05/01/2026 14:35", "action": "Transfer", "details": "SEPA transfer of 150.00 EUR", "ip": "86.123.45.67"},
            {"time": "05/01/2026 14:40", "action": "Card Block", "details": "Temporary card block activated", "ip": "86.123.45.67"},
            {"time": "04/01/2026 09:15", "action": "Login", "details": "Successful login from Lyon, FR", "ip": "92.184.12.34"},
            {"time": "03/01/2026 18:22", "action": "Beneficiary", "details": "New beneficiary added", "ip": "86.123.45.67"},
        ]

        for log in logs:
            col1, col2, col3 = st.columns([2, 4, 2])
            with col1:
                st.caption(log['time'])
            with col2:
                st.markdown(f"**{log['action']}**")
                st.caption(log['details'])
            with col3:
                st.caption(f"IP: {log['ip']}")
            st.divider()

    with tab2:
        st.markdown("### Security Alerts")

        alerts = [
            {"time": "02/01/2026 22:45", "type": "Unusual Location", "desc": "Login attempt from Germany", "status": "Blocked", "risk": "High"},
            {"time": "28/12/2025 15:30", "type": "Large Transaction", "desc": "Transfer > 5,000 EUR detected", "status": "Verified", "risk": "Medium"},
        ]

        for alert in alerts:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            with col1:
                st.caption(alert['time'])
                if alert['risk'] == 'High':
                    st.error(f"Risk: {alert['risk']}")
                else:
                    st.warning(f"Risk: {alert['risk']}")
            with col2:
                st.markdown(f"**{alert['type']}**")
                st.caption(alert['desc'])
            with col3:
                if alert['status'] == 'Blocked':
                    st.error(alert['status'])
                else:
                    st.success(alert['status'])
            with col4:
                st.button("Details", key=f"alert_{alert['time']}")
            st.divider()

        st.markdown("### Security Settings")
        col1, col2 = st.columns(2)
        with col1:
            st.toggle("Two-Factor Authentication", value=True)
            st.toggle("Login Notifications", value=True)
        with col2:
            st.toggle("Transaction Alerts", value=True)
            st.toggle("Unusual Activity Alerts", value=True)
