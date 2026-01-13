"""
Cards page
"""

import streamlit as st

from .common import page_header


def render_cards():
    """Render cards page"""
    page_header("Cards")

    st.info("Card management coming soon!")

    st.markdown("### Your Cards")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 24px; color: white; height: 200px;">
            <div style="font-size: 12px; opacity: 0.8;">VISA</div>
            <div style="font-size: 24px; letter-spacing: 4px; margin: 24px 0;">**** **** **** 4242</div>
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <div style="font-size: 10px; opacity: 0.8;">CARD HOLDER</div>
                    <div>JOHN DOE</div>
                </div>
                <div>
                    <div style="font-size: 10px; opacity: 0.8;">EXPIRES</div>
                    <div>12/27</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
