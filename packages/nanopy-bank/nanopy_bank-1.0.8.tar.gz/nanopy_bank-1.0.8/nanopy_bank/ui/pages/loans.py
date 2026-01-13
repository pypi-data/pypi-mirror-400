"""
Loans page
"""

import streamlit as st

from .common import page_header


def render_loans():
    """Render loans page"""
    page_header("Loans & Products")

    tab1, tab2, tab3 = st.tabs(["My Loans", "Savings Products", "Insurance"])

    with tab1:
        st.markdown("### Active Loans")

        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); border-radius: 16px; padding: 24px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <div style="color: #00d4ff; font-size: 12px; text-transform: uppercase;">Personal Loan</div>
                    <div style="color: white; font-size: 24px; font-weight: bold; margin: 8px 0;">15,000.00 EUR</div>
                    <div style="color: #aaa; font-size: 14px;">Travaux maison</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #00ff88; font-size: 18px; font-weight: bold;">5.50%</div>
                    <div style="color: #aaa; font-size: 12px;">Annual Rate</div>
                </div>
            </div>
            <div style="margin-top: 20px; background: rgba(255,255,255,0.1); border-radius: 8px; height: 8px;">
                <div style="background: linear-gradient(90deg, #00d4ff, #00ff88); border-radius: 8px; height: 8px; width: 35%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 8px; color: #888; font-size: 12px;">
                <span>Paid: 5,250.00 EUR (35%)</span>
                <span>Remaining: 9,750.00 EUR</span>
            </div>
            <div style="display: flex; gap: 20px; margin-top: 20px; color: white; font-size: 14px;">
                <div><span style="color: #888;">Monthly:</span> 350.00 EUR</div>
                <div><span style="color: #888;">Duration:</span> 48 months</div>
                <div><span style="color: #888;">Next payment:</span> 05/02/2026</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Request New Loan"):
            with st.form("loan_request"):
                col1, col2 = st.columns(2)
                with col1:
                    st.selectbox("Loan Type", ["Personal", "Auto", "Mortgage", "Student"])
                    st.number_input("Amount", min_value=1000, max_value=500000, value=10000, step=1000)
                with col2:
                    st.slider("Duration (months)", 12, 360, 48)
                    st.text_input("Purpose")

                if st.form_submit_button("Submit Request"):
                    st.info("Your loan request has been submitted for review.")

    with tab2:
        st.markdown("### Savings Products")

        savings = [
            {"name": "Livret A", "balance": "15,000.00", "rate": "3.00%", "ceiling": "22,950.00"},
            {"name": "LDDS", "balance": "8,500.00", "rate": "3.00%", "ceiling": "12,000.00"},
        ]

        for s in savings:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.markdown(f"**{s['name']}**")
            with col2:
                st.markdown(f":green[{s['balance']} EUR]")
            with col3:
                st.markdown(f"Rate: {s['rate']}")
            with col4:
                st.caption(f"Ceiling: {s['ceiling']} EUR")
            st.divider()

        with st.expander("Open New Savings Account"):
            with st.form("new_savings"):
                st.selectbox("Product", ["Livret A", "LDDS", "LEP", "PEL"])
                st.number_input("Initial Deposit", min_value=10, value=100)
                if st.form_submit_button("Open Account"):
                    st.success("Savings account opened!")

    with tab3:
        st.markdown("### Insurance Products")

        insurances = [
            {"name": "Home Insurance", "type": "Habitation", "premium": "35.00/month", "status": "Active"},
            {"name": "Loan Insurance", "type": "Emprunteur", "premium": "25.00/month", "status": "Active"},
        ]

        for ins in insurances:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.markdown(f"**{ins['name']}**")
            with col2:
                st.caption(ins['type'])
            with col3:
                st.markdown(f":blue[{ins['premium']}]")
            with col4:
                st.success(ins['status'])
            st.divider()
