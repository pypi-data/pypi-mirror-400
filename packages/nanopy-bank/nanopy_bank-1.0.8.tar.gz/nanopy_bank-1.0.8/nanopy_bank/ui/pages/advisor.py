"""
Advisor page - Employee/Conseiller view
"""

import streamlit as st
import pandas as pd

from .common import page_header, format_currency


def render_advisor():
    """Render advisor dashboard"""
    page_header("Espace Conseiller")

    bank = st.session_state.bank

    tab1, tab2, tab3, tab4 = st.tabs(["Mes Clients", "Demandes", "Objectifs", "Agenda"])

    with tab1:
        st.markdown("### Portefeuille Clients")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Clients geres", len(bank.customers) or 42)
        with col2:
            st.metric("Encours total", "2.4M EUR")
        with col3:
            st.metric("RDV ce mois", 18)

        st.divider()

        # Client list
        clients = [
            {"name": "Jean Dupont", "status": "Premium", "balance": "45,000 EUR", "products": 4, "last_contact": "02/01/2026"},
            {"name": "Marie Martin", "status": "Standard", "balance": "12,500 EUR", "products": 2, "last_contact": "28/12/2025"},
            {"name": "Pierre Bernard", "status": "Pro", "balance": "85,000 EUR", "products": 6, "last_contact": "05/01/2026"},
            {"name": "Sophie Petit", "status": "Jeune", "balance": "2,300 EUR", "products": 1, "last_contact": "15/12/2025"},
        ]

        for client in clients:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 1])
            with col1:
                st.markdown(f"**{client['name']}**")
            with col2:
                if client['status'] == 'Premium':
                    st.success(client['status'])
                elif client['status'] == 'Pro':
                    st.info(client['status'])
                else:
                    st.caption(client['status'])
            with col3:
                st.markdown(f":green[{client['balance']}]")
            with col4:
                st.caption(f"{client['products']} produits")
            with col5:
                st.button("Fiche", key=f"client_{client['name']}")
            st.divider()

    with tab2:
        st.markdown("### Demandes en attente")

        requests = [
            {"client": "Jean Dupont", "type": "Pret personnel", "amount": "15,000 EUR", "date": "04/01/2026", "priority": "High"},
            {"client": "Pierre Bernard", "type": "Augmentation decouvert", "amount": "5,000 EUR", "date": "03/01/2026", "priority": "Medium"},
            {"client": "Marie Martin", "type": "Carte Gold", "amount": "-", "date": "02/01/2026", "priority": "Low"},
        ]

        for req in requests:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 2])
            with col1:
                st.markdown(f"**{req['client']}**")
                st.caption(req['type'])
            with col2:
                st.markdown(req['amount'])
            with col3:
                st.caption(req['date'])
            with col4:
                if req['priority'] == 'High':
                    st.error("Urgent")
                elif req['priority'] == 'Medium':
                    st.warning("Normal")
                else:
                    st.info("Faible")
            with col5:
                c1, c2 = st.columns(2)
                with c1:
                    st.button("Approuver", key=f"approve_{req['client']}", type="primary")
                with c2:
                    st.button("Refuser", key=f"reject_{req['client']}")
            st.divider()

    with tab3:
        st.markdown("### Objectifs Commerciaux")

        objectives = [
            {"name": "Ouvertures de compte", "current": 12, "target": 15, "percent": 80},
            {"name": "Credits accordes", "current": 450000, "target": 500000, "percent": 90},
            {"name": "Assurances vendues", "current": 8, "target": 12, "percent": 67},
            {"name": "Cartes Premium", "current": 5, "target": 8, "percent": 62},
        ]

        for obj in objectives:
            st.markdown(f"**{obj['name']}**")
            st.progress(obj['percent'] / 100)
            st.caption(f"{obj['current']:,} / {obj['target']:,} ({obj['percent']}%)")
            st.divider()

    with tab4:
        st.markdown("### Agenda")

        appointments = [
            {"time": "09:00", "client": "Jean Dupont", "type": "Revue annuelle", "location": "Agence"},
            {"time": "11:00", "client": "Marie Martin", "type": "Simulation pret", "location": "Telephone"},
            {"time": "14:30", "client": "Pierre Bernard", "type": "Bilan pro", "location": "Agence"},
            {"time": "16:00", "client": "Sophie Petit", "type": "Premier RDV", "location": "Agence"},
        ]

        for apt in appointments:
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col1:
                st.markdown(f"**{apt['time']}**")
            with col2:
                st.markdown(apt['client'])
            with col3:
                st.caption(apt['type'])
            with col4:
                st.caption(apt['location'])
            st.divider()

        with st.expander("Planifier un RDV"):
            with st.form("new_appointment"):
                col1, col2 = st.columns(2)
                with col1:
                    st.date_input("Date")
                    st.time_input("Heure")
                with col2:
                    st.selectbox("Client", ["Jean Dupont", "Marie Martin", "Pierre Bernard", "Sophie Petit"])
                    st.selectbox("Type", ["Revue annuelle", "Simulation pret", "Premier RDV", "Reclamation"])
                if st.form_submit_button("Planifier"):
                    st.success("RDV planifie!")
