"""
Branches page
"""

import streamlit as st

from .common import page_header


def render_branches():
    """Render branches and employees page"""
    page_header("Branches & Contact")

    tab1, tab2 = st.tabs(["Our Branches", "Contact Advisor"])

    with tab1:
        st.markdown("### Find a Branch")

        st.text_input("Search by city or postal code", placeholder="Paris, 75001...")

        branches = [
            {"name": "Paris Opera", "address": "1 Place de l'Opera, 75009 Paris", "phone": "+33 1 42 68 00 00", "open": True},
            {"name": "Lyon Part-Dieu", "address": "17 Rue de la Part-Dieu, 69003 Lyon", "phone": "+33 4 72 00 00 00", "open": True},
            {"name": "Marseille Vieux-Port", "address": "42 Quai du Port, 13002 Marseille", "phone": "+33 4 91 00 00 00", "open": False},
        ]

        for branch in branches:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{branch['name']}**")
                st.caption(branch['address'])
            with col2:
                st.caption(branch['phone'])
            with col3:
                if branch['open']:
                    st.success("Open")
                else:
                    st.error("Closed")
            st.divider()

    with tab2:
        st.markdown("### Your Advisor")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("""
            <div style="background: #1e1e2f; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; font-size: 40px;">
                👤
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("**Thomas Moreau**")
            st.caption("Personal Banking Advisor")
            st.markdown("Email: thomas.moreau@nanopybank.fr")
            st.markdown("Phone: +33 1 42 68 00 01")

        st.divider()

        st.markdown("### Send a Message")
        with st.form("contact_form"):
            st.text_input("Subject")
            st.text_area("Message")
            if st.form_submit_button("Send"):
                st.success("Message sent to your advisor!")
