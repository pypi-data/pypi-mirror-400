"""
Holding page - Group management view for Nova x Genesis SASU
"""

import streamlit as st
from decimal import Decimal
from datetime import datetime, date

from .common import page_header

try:
    from ...data.demo import get_demo_holding_data
except ImportError:
    from nanopy_bank.data.demo import get_demo_holding_data


def get_holding_data():
    """Get or create holding data in session state"""
    if "holding_data" not in st.session_state:
        st.session_state.holding_data = get_demo_holding_data()
    return st.session_state.holding_data


def format_amount(amount: Decimal, currency: str = "EUR") -> str:
    """Format amount with thousands separator"""
    return f"{amount:,.2f} {currency}".replace(",", " ").replace(".", ",").replace(" ", " ")


def render_holding(tab: str = "dashboard"):
    """Render holding/group management dashboard"""
    data = get_holding_data()
    holding = data["holding"]

    page_header(holding["name"])

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border: 1px solid #333; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <div style="color: #00ff88; font-size: 12px; text-transform: uppercase;">{holding['legal_name']}</div>
        <div style="color: white; font-size: 24px; font-weight: bold; margin: 8px 0;">SIREN: {holding['siren']} | LEI: {holding['lei']}</div>
    </div>
    """, unsafe_allow_html=True)

    if tab == "dashboard":
        render_dashboard_tab(data)
    elif tab == "tresorerie":
        render_tresorerie_tab(data)
    elif tab == "investissements":
        render_investissements_tab(data)
    elif tab == "assurances":
        render_assurances_tab(data)
    elif tab == "filiales":
        render_filiales_tab(data)
    elif tab == "consolidation":
        render_consolidation_tab(data)
    elif tab == "risques":
        render_risques_tab(data)
    elif tab == "gouvernance":
        render_gouvernance_tab(data)


def render_dashboard_tab(data):
    """Dashboard with KPIs"""
    st.markdown("### Vue d'ensemble")

    # Calculate totals
    total_treasury = data["accounts"]["principal"]["balance"] + data["accounts"]["tresorerie"]["balance"]
    total_assets = sum(s["assets"] for s in data["subsidiaries"])
    total_employees = sum(s["employees"] for s in data["subsidiaries"])
    pool_net = sum(s["pool_balance"] for s in data["subsidiaries"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tresorerie Holding", format_amount(total_treasury))
    with col2:
        st.metric("Actifs Consolides", f"{total_assets/1000000000:.1f}B EUR")
    with col3:
        st.metric("Effectif Groupe", f"{total_employees:,}".replace(",", " "))
    with col4:
        st.metric("Position Cash Pool", format_amount(pool_net))

    st.divider()

    # Recent activity
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Filiales")
        for sub in data["subsidiaries"][:3]:
            status_color = "#00ff88" if sub["status"] == "active" else "#ffd93d"
            st.markdown(f"""
            <div style="background: #1e1e2f; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: white; font-weight: bold;">{sub['name']}</span>
                    <span style="color: {status_color};">{sub['ownership']}%</span>
                </div>
                <div style="color: #888; font-size: 12px;">{sub['type']}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Prets Intra-Groupe")
        for loan in data["intra_group_loans"][:3]:
            st.markdown(f"""
            <div style="background: #1e1e2f; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: white; font-weight: bold;">{loan['borrower']}</span>
                    <span style="color: #00d4ff;">{format_amount(loan['outstanding'])}</span>
                </div>
                <div style="color: #888; font-size: 12px;">Taux: {loan['rate']}% | Echeance: {loan['maturity'].strftime('%d/%m/%Y')}</div>
            </div>
            """, unsafe_allow_html=True)


def render_tresorerie_tab(data):
    """Treasury management"""
    st.markdown("### Comptes Tresorerie")

    col1, col2 = st.columns(2)

    for key, account in data["accounts"].items():
        with col1 if key == "principal" else col2:
            color = "#00ff88" if key == "principal" else "#00d4ff"
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1b4e2d, #0d2818); border: 1px solid {color}; border-radius: 12px; padding: 20px;">
                <div style="color: {color}; font-size: 12px; text-transform: uppercase;">{account['name']}</div>
                <div style="color: white; font-size: 11px; margin: 4px 0;">{account['iban']}</div>
                <div style="color: {color}; font-size: 28px; font-weight: bold; margin-top: 12px;">{format_amount(account['balance'])}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Cash pooling
    st.markdown("### Cash Pooling - Position Nette")

    for sub in data["subsidiaries"]:
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            st.markdown(f"**{sub['name']}**")
            st.caption(f"FR76 NANP {sub['id'][-4:]} xxxx")
        with col2:
            balance = sub["pool_balance"]
            if balance >= 0:
                st.markdown(f":green[+{format_amount(balance)}]")
            else:
                st.markdown(f":red[{format_amount(balance)}]")
        with col3:
            st.caption(f"Limite: {format_amount(sub['pool_limit'])}")
        with col4:
            if st.button("Virement", key=f"pool_transfer_{sub['id']}"):
                st.session_state.show_transfer_modal = sub['id']

    # Transfer modal
    if "show_transfer_modal" in st.session_state and st.session_state.show_transfer_modal:
        sub_id = st.session_state.show_transfer_modal
        sub = next((s for s in data["subsidiaries"] if s["id"] == sub_id), None)
        if sub:
            with st.expander(f"Virement vers/depuis {sub['name']}", expanded=True):
                direction = st.radio("Direction", ["Holding -> Filiale", "Filiale -> Holding"], key=f"dir_{sub_id}")
                amount = st.number_input("Montant (EUR)", min_value=0.0, max_value=10000000.0, step=1000.0, key=f"amt_{sub_id}")
                motif = st.text_input("Motif", key=f"motif_{sub_id}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Annuler", key=f"cancel_{sub_id}"):
                        del st.session_state.show_transfer_modal
                        st.rerun()
                with col2:
                    if st.button("Valider", type="primary", key=f"validate_{sub_id}"):
                        if amount > 0 and motif:
                            # Process transfer
                            if "Holding -> Filiale" in direction:
                                data["accounts"]["principal"]["balance"] -= Decimal(str(amount))
                                sub["pool_balance"] += Decimal(str(amount))
                            else:
                                data["accounts"]["principal"]["balance"] += Decimal(str(amount))
                                sub["pool_balance"] -= Decimal(str(amount))

                            data["transactions"].append({
                                "date": datetime.now(),
                                "type": "pool_transfer",
                                "direction": direction,
                                "subsidiary": sub["name"],
                                "amount": Decimal(str(amount)),
                                "motif": motif,
                            })

                            del st.session_state.show_transfer_modal
                            st.success(f"Virement de {format_amount(Decimal(str(amount)))} effectue")
                            st.rerun()
                        else:
                            st.error("Veuillez remplir tous les champs")

    st.divider()

    pool_net = sum(s["pool_balance"] for s in data["subsidiaries"])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Position Nette Pool", format_amount(pool_net))
    with col2:
        st.metric("Taux Crediteur", f"{data['pool_rates']['credit']}%")
    with col3:
        st.metric("Taux Debiteur", f"{data['pool_rates']['debit']}%")

    st.divider()

    # Intra-group loans
    st.markdown("### Prets Intra-Groupe")

    for loan in data["intra_group_loans"]:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 2, 1])
        with col1:
            st.markdown(f"**{loan['borrower']}**")
            st.caption(f"Ref: {loan['id']}")
        with col2:
            st.markdown(f":blue[{format_amount(loan['outstanding'])}]")
            st.caption(f"Principal: {format_amount(loan['principal'])}")
        with col3:
            st.caption(f"Taux: {loan['rate']}%")
        with col4:
            st.caption(f"Echeance: {loan['maturity'].strftime('%d/%m/%Y')}")
        with col5:
            if st.button("Details", key=f"loan_{loan['id']}"):
                st.info(f"Debut: {loan['start_date'].strftime('%d/%m/%Y')}\nRembourse: {format_amount(loan['principal'] - loan['outstanding'])}")
        st.divider()

    total_loans = sum(l["outstanding"] for l in data["intra_group_loans"])
    st.metric("Total Encours Prets", format_amount(total_loans))

    # New loan button
    if st.button("Nouveau Pret Intra-Groupe", type="primary"):
        st.session_state.show_new_loan = True

    if st.session_state.get("show_new_loan"):
        with st.expander("Nouveau Pret", expanded=True):
            borrower = st.selectbox("Emprunteur", [s["name"] for s in data["subsidiaries"]])
            principal = st.number_input("Montant (EUR)", min_value=100000.0, max_value=50000000.0, step=100000.0)
            rate = st.number_input("Taux annuel (%)", min_value=0.5, max_value=5.0, step=0.25, value=1.25)
            maturity = st.date_input("Date d'echeance", min_value=date.today())

            if st.button("Creer le pret", type="primary"):
                sub = next((s for s in data["subsidiaries"] if s["name"] == borrower), None)
                if sub:
                    new_loan = {
                        "id": f"IGL{len(data['intra_group_loans'])+1:03d}",
                        "borrower": borrower,
                        "borrower_id": sub["id"],
                        "principal": Decimal(str(principal)),
                        "outstanding": Decimal(str(principal)),
                        "rate": Decimal(str(rate)),
                        "start_date": date.today(),
                        "maturity": maturity,
                        "status": "active",
                    }
                    data["intra_group_loans"].append(new_loan)
                    data["accounts"]["principal"]["balance"] -= Decimal(str(principal))
                    del st.session_state.show_new_loan
                    st.success(f"Pret de {format_amount(Decimal(str(principal)))} accorde a {borrower}")
                    st.rerun()


def render_filiales_tab(data):
    """Subsidiaries management"""
    st.markdown("### Filiales du Groupe")

    for sub in data["subsidiaries"]:
        with st.expander(f"{sub['name']} ({sub['ownership']}%)", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Type:** {sub['type']}")
                st.markdown(f"**Statut:** {'Actif' if sub['status'] == 'active' else 'Startup'}")
            with col2:
                st.markdown(f"**Actifs:** {sub['assets']/1000000:.0f}M EUR")
                st.markdown(f"**Effectif:** {sub['employees']}")
            with col3:
                st.markdown(f"**Participation:** {sub['ownership']}%")
                pool_color = "green" if sub["pool_balance"] >= 0 else "red"
                st.markdown(f"**Position Pool:** :{pool_color}[{format_amount(sub['pool_balance'])}]")

            # Actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Voir details", key=f"details_{sub['id']}"):
                    st.info(f"ID: {sub['id']}\nLimite pool: {format_amount(sub['pool_limit'])}")
            with col2:
                if st.button("Historique", key=f"history_{sub['id']}"):
                    txs = [t for t in data["transactions"] if t.get("subsidiary") == sub["name"]]
                    if txs:
                        for tx in txs[-5:]:
                            st.write(f"{tx['date'].strftime('%d/%m/%Y')} - {tx['type']} - {format_amount(tx['amount'])}")
                    else:
                        st.info("Aucune transaction")

    st.divider()

    # Dividends
    st.markdown("### Dividendes")

    for div in data["dividends"]:
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        with col1:
            st.markdown(f"**{div['subsidiary']}**")
            st.caption(f"Exercice {div['year']}")
        with col2:
            st.caption(f"Brut: {format_amount(div['gross'])}")
        with col3:
            st.caption(f"Retenue: {format_amount(div['tax'])}")
        with col4:
            st.markdown(f":green[Net: {format_amount(div['net'])}]")
        with col5:
            status_map = {"paid": ("Paye", "success"), "approved": ("Approuve", "info"), "declared": ("Declare", "warning")}
            label, style = status_map.get(div["status"], ("?", "info"))
            if style == "success":
                st.success(label)
            elif style == "warning":
                st.warning(label)
            else:
                st.info(label)

    total_div = sum(d["net"] for d in data["dividends"])
    st.metric("Total Dividendes 2025", format_amount(total_div))


def render_investissements_tab(data):
    """Sovereign bonds portfolio management"""
    st.markdown("### Portefeuille Obligataire Souverain")

    bonds = data.get("sovereign_bonds", [])
    available = data.get("available_bonds", [])

    # Separate high-yield emerging bonds from core bonds
    emerging_countries = ["UA", "PL", "RO"]  # Ukraine, Poland, Romania
    emerging_bonds = [b for b in bonds if b["country"] in emerging_countries]
    core_bonds = [b for b in bonds if b["country"] not in emerging_countries]

    # Calculate portfolio value
    total_nominal = sum(b["nominal"] for b in bonds) if bonds else Decimal("0")
    total_market_value = sum(b["nominal"] * b["current_price"] / 100 for b in bonds) if bonds else Decimal("0")
    total_cost = sum(b["nominal"] * b["purchase_price"] / 100 for b in bonds) if bonds else Decimal("0")
    pnl = total_market_value - total_cost
    annual_coupons = sum(b["nominal"] * b["coupon"] / 100 for b in bonds) if bonds else Decimal("0")

    # Emerging bonds specific
    emerging_nominal = sum(b["nominal"] for b in emerging_bonds) if emerging_bonds else Decimal("0")
    emerging_coupons = sum(b["nominal"] * b["coupon"] / 100 for b in emerging_bonds) if emerging_bonds else Decimal("0")
    emerging_pnl = sum(b["nominal"] * (b["current_price"] - b["purchase_price"]) / 100 for b in emerging_bonds) if emerging_bonds else Decimal("0")

    # Portfolio KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Valeur Nominale", format_amount(total_nominal))
    with col2:
        st.metric("Valeur de Marche", format_amount(total_market_value))
    with col3:
        pnl_delta = f"{'+' if pnl >= 0 else ''}{float(pnl/total_cost)*100:.2f}%" if total_cost > 0 else "0%"
        st.metric("P&L Latent", format_amount(pnl), pnl_delta)
    with col4:
        st.metric("Coupons Annuels", format_amount(annual_coupons))

    st.divider()

    # ==================== SECTION EMERGENTS ====================
    if emerging_bonds:
        st.markdown("### Obligations Emergentes (Haut Rendement)")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4a1a1a, #1a1a2e); border: 1px solid #ff6b6b; border-radius: 12px; padding: 15px; margin-bottom: 20px;">
            <div style="color: #ff6b6b; font-size: 12px; text-transform: uppercase;">Ukraine (War Bonds), Pologne, Roumanie</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            emerging_pct = float(emerging_nominal / total_nominal * 100) if total_nominal > 0 else 0
            st.metric("Exposition Emergents", format_amount(emerging_nominal), f"{emerging_pct:.1f}% du portefeuille")
        with col2:
            st.metric("Coupons Emergents", format_amount(emerging_coupons), "annuels")
        with col3:
            emerging_pnl_pct = f"{'+' if emerging_pnl >= 0 else ''}{float(emerging_pnl / (emerging_nominal * Decimal('0.5')) * 100):.1f}%" if emerging_nominal > 0 else "0%"
            st.metric("P&L Emergents", format_amount(emerging_pnl), emerging_pnl_pct)
        with col4:
            avg_yield = sum(b["coupon"] for b in emerging_bonds) / len(emerging_bonds) if emerging_bonds else Decimal("0")
            st.metric("Rendement Moyen", f"{avg_yield:.2f}%", "brut")

        # Emerging bonds details
        for bond in emerging_bonds:
            market_val = bond["nominal"] * bond["current_price"] / 100
            cost_val = bond["nominal"] * bond["purchase_price"] / 100
            bond_pnl = market_val - cost_val
            pnl_pct = float(bond_pnl / cost_val * 100) if cost_val > 0 else 0

            # Risk color and label based on country
            if bond["country"] == "UA":
                risk_color = "#ff6b6b"
                risk_label = "WAR BOND"
            elif bond["country"] == "RO":
                risk_color = "#ffd93d"
                risk_label = "HIGH YIELD"
            else:
                risk_color = "#00d4ff"
                risk_label = "INVESTMENT GRADE"

            st.markdown(f"""
            <div style="background: #1e1e2f; border-left: 4px solid {risk_color}; padding: 12px; border-radius: 0 8px 8px 0; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: white; font-weight: bold;">{bond['country']} | {bond['name']}</span>
                        <span style="background: {risk_color}; color: black; font-size: 10px; padding: 2px 6px; border-radius: 4px; margin-left: 10px;">{risk_label}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #00d4ff;">{format_amount(bond['nominal'])} nominal</div>
                        <div style="color: {'#00ff88' if bond_pnl >= 0 else '#ff6b6b'};">P&L: {format_amount(bond_pnl)} ({pnl_pct:+.1f}%)</div>
                    </div>
                </div>
                <div style="color: #888; font-size: 12px; margin-top: 8px;">
                    Coupon: {bond['coupon']}% | Prix achat: {bond['purchase_price']}% | Prix actuel: {bond['current_price']}% | Echeance: {bond['maturity'].strftime('%d/%m/%Y')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

    # ==================== ALIMENTATION COMPTE TITRES (en premier) ====================
    st.markdown("### Alimentation Compte Titres")
    st.caption(f"Solde compte principal: {format_amount(data['accounts']['principal']['balance'])} | Solde compte titres: {format_amount(data['accounts']['titres']['balance'])}")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        transfer_amount = st.number_input(
            "Montant a transferer (EUR)",
            min_value=100000.0,
            max_value=float(data["accounts"]["principal"]["balance"]),
            step=100000.0,
            value=1000000.0,
            key="fund_titres"
        )
    with col2:
        if st.button("Alimenter Compte Titres", type="primary", key="btn_fund"):
            amount = Decimal(str(transfer_amount))
            data["accounts"]["principal"]["balance"] -= amount
            data["accounts"]["titres"]["balance"] += amount
            data.get("transactions", []).append({
                "date": datetime.now(),
                "type": "internal_transfer",
                "from": "principal",
                "to": "titres",
                "amount": amount,
                "motif": "Alimentation compte titres",
            })
            st.success(f"Transfert de {format_amount(amount)} effectue")
            st.rerun()
    with col3:
        if st.button("Retirer vers Principal", key="btn_withdraw"):
            if data["accounts"]["titres"]["balance"] >= Decimal(str(transfer_amount)):
                amount = Decimal(str(transfer_amount))
                data["accounts"]["titres"]["balance"] -= amount
                data["accounts"]["principal"]["balance"] += amount
                st.success(f"Retrait de {format_amount(amount)} effectue")
                st.rerun()
            else:
                st.error("Solde insuffisant")

    st.divider()

    # ==================== FORMULAIRE D'ACHAT ====================
    st.markdown("### Acheter des Obligations")

    # Filter by region
    region = st.radio("Region", ["Toutes", "Zone Euro", "Hors Zone Euro"], horizontal=True, key="region_filter")

    eurozone = ["FR", "DE", "IT", "ES", "NL", "BE", "AT", "PT", "IE", "FI"]
    filtered = available
    if region == "Zone Euro":
        filtered = [b for b in available if b["country"] in eurozone]
    elif region == "Hors Zone Euro":
        filtered = [b for b in available if b["country"] not in eurozone]

    # Bond selection
    bond_options = {f"{b['country']} - {b['name']} (Rdt: {b['yield']}%)": b['isin'] for b in filtered}

    if bond_options:
        selected_label = st.selectbox("Selectionnez une obligation", list(bond_options.keys()), key="select_bond")
        selected_isin = bond_options[selected_label]
        selected_bond = next((b for b in filtered if b["isin"] == selected_isin), None)

        if selected_bond:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**{selected_bond['name']}**\nISIN: {selected_bond['isin']}")
            with col2:
                st.info(f"**Coupon:** {selected_bond['coupon']}%\n**Echeance:** {selected_bond['maturity'].strftime('%d/%m/%Y')}")
            with col3:
                st.info(f"**Prix:** {selected_bond['current_price']}%\n**Rendement:** {selected_bond['yield']}%")

            col1, col2 = st.columns(2)
            with col1:
                buy_nominal = st.number_input(
                    "Nominal a acheter (EUR)",
                    min_value=100000.0,
                    max_value=10000000.0,
                    step=100000.0,
                    value=1000000.0,
                    key="buy_nominal_input"
                )
                buy_cost = Decimal(str(buy_nominal)) * selected_bond["current_price"] / 100
                st.caption(f"Cout total: **{format_amount(buy_cost)}**")

            with col2:
                cash_available = data["accounts"]["titres"]["balance"]
                st.caption(f"Cash disponible: {format_amount(cash_available)}")

                if st.button("Acheter", type="primary", key="btn_buy_bond", disabled=buy_cost > cash_available):
                    if buy_cost > cash_available:
                        st.error("Fonds insuffisants! Alimentez d'abord le compte titres.")
                    else:
                        new_bond = {
                            "isin": selected_bond["isin"],
                            "name": selected_bond["name"],
                            "country": selected_bond["country"],
                            "country_name": selected_bond["country_name"],
                            "coupon": selected_bond["coupon"],
                            "maturity": selected_bond["maturity"],
                            "nominal": Decimal(str(buy_nominal)),
                            "purchase_price": selected_bond["current_price"],
                            "current_price": selected_bond["current_price"],
                            "purchase_date": date.today(),
                            "quantity": int(buy_nominal / 100000),
                        }
                        data["sovereign_bonds"].append(new_bond)
                        data["accounts"]["titres"]["balance"] -= buy_cost
                        if "bond_transactions" not in data:
                            data["bond_transactions"] = []
                        data["bond_transactions"].append({
                            "date": datetime.now(),
                            "type": "buy",
                            "isin": selected_bond["isin"],
                            "name": selected_bond["name"],
                            "nominal": Decimal(str(buy_nominal)),
                            "price": selected_bond["current_price"],
                            "amount": buy_cost,
                        })
                        st.success(f"Achat de {format_amount(Decimal(str(buy_nominal)))} nominal execute!")
                        st.rerun()

                if buy_cost > cash_available:
                    st.warning(f"Il manque {format_amount(buy_cost - cash_available)} sur le compte titres")

    st.divider()

    # ==================== PORTEFEUILLE ACTUEL ====================
    st.markdown("### Repartition Geographique")

    if bonds:
        countries = {}
        for bond in bonds:
            country = bond["country_name"]
            if country not in countries:
                countries[country] = Decimal("0")
            countries[country] += bond["nominal"]

        for country, nominal in sorted(countries.items(), key=lambda x: x[1], reverse=True):
            pct = float(nominal / total_nominal * 100) if total_nominal > 0 else 0
            col1, col2 = st.columns([1, 3])
            with col1:
                flag_map = {"France": "FR", "Allemagne": "DE", "Italie": "IT", "Espagne": "ES", "Etats-Unis": "US", "Royaume-Uni": "GB", "Japon": "JP", "Suisse": "CH", "Pays-Bas": "NL", "Belgique": "BE"}
                flag = flag_map.get(country, "EU")
                st.markdown(f"**{flag} {country}**")
                st.caption(format_amount(nominal))
            with col2:
                st.progress(pct / 100)
                st.caption(f"{pct:.1f}%")
    else:
        st.info("Aucune obligation en portefeuille")

    st.divider()

    # ==================== POSITIONS ACTUELLES ====================
    st.markdown("### Positions Actuelles")

    if bonds:
        for idx, bond in enumerate(bonds):
            market_val = bond["nominal"] * bond["current_price"] / 100
            cost_val = bond["nominal"] * bond["purchase_price"] / 100
            bond_pnl = market_val - cost_val
            pnl_pct = float(bond_pnl / cost_val * 100) if cost_val > 0 else 0

            with st.expander(f"{bond['country']} | {bond['name']} | {format_amount(bond['nominal'])} nominal", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"**ISIN:** {bond['isin']}")
                    st.markdown(f"**Nominal:** {format_amount(bond['nominal'])}")
                with col2:
                    st.markdown(f"**Coupon:** {bond['coupon']}%")
                    st.markdown(f"**Echeance:** {bond['maturity'].strftime('%d/%m/%Y')}")
                with col3:
                    st.markdown(f"**Prix achat:** {bond['purchase_price']}%")
                    st.markdown(f"**Prix actuel:** {bond['current_price']}%")
                with col4:
                    pnl_color = "green" if bond_pnl >= 0 else "red"
                    st.markdown(f"**Valeur marche:** {format_amount(market_val)}")
                    st.markdown(f"**P&L:** :{pnl_color}[{format_amount(bond_pnl)} ({pnl_pct:+.2f}%)]")

                # Vente
                st.markdown("---")
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    sell_pct = st.slider(f"% a vendre", 10, 100, 100, 10, key=f"sell_pct_{idx}")
                    sell_nominal = bond["nominal"] * sell_pct / 100
                    sell_value = sell_nominal * bond["current_price"] / 100
                    st.caption(f"Vente: {format_amount(sell_nominal)} nominal = {format_amount(sell_value)}")
                with col2:
                    if st.button("Vendre", key=f"sell_btn_{idx}", type="secondary"):
                        if sell_pct == 100:
                            data["sovereign_bonds"].remove(bond)
                        else:
                            bond["nominal"] -= sell_nominal
                        data["accounts"]["titres"]["balance"] += sell_value
                        if "bond_transactions" not in data:
                            data["bond_transactions"] = []
                        data["bond_transactions"].append({
                            "date": datetime.now(),
                            "type": "sell",
                            "isin": bond["isin"],
                            "name": bond["name"],
                            "nominal": sell_nominal,
                            "price": bond["current_price"],
                            "amount": sell_value,
                        })
                        st.success(f"Vente executee: {format_amount(sell_value)}")
                        st.rerun()
                with col3:
                    txs = [t for t in data.get("bond_transactions", []) if t.get("isin") == bond["isin"]]
                    if txs:
                        st.caption(f"{len(txs)} transaction(s)")
    else:
        st.info("Aucune position. Achetez des obligations ci-dessus.")


def render_assurances_tab(data):
    """Group insurance management"""
    st.markdown("### Assurances Groupe")

    insurances = data.get("insurances", [])
    claims = data.get("claims", [])

    # Calculate totals
    total_coverage = sum(ins["coverage"] for ins in insurances) if insurances else Decimal("0")
    total_premiums = sum(ins["premium"] for ins in insurances) if insurances else Decimal("0")
    active_policies = len([ins for ins in insurances if ins["status"] == "active"])

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Couverture Totale", format_amount(total_coverage))
    with col2:
        st.metric("Primes Annuelles", format_amount(total_premiums))
    with col3:
        st.metric("Polices Actives", str(active_policies))
    with col4:
        pending_claims = len([c for c in claims if c["status"] == "pending"])
        st.metric("Sinistres en cours", str(pending_claims))

    st.divider()

    # Insurance by type
    st.markdown("### Polices d'Assurance")

    type_labels = {
        "D&O": ("RC Dirigeants", "#7b2cbf"),
        "RC_PRO": ("RC Professionnelle", "#00d4ff"),
        "CYBER": ("Cyber", "#ff6b6b"),
        "PROPERTY": ("Immobilier", "#00ff88"),
        "KEY_MAN": ("Homme-Cle", "#ffd93d"),
        "CDS": ("Credit Default Swap", "#ff6b6b"),
    }

    for ins in insurances:
        type_info = type_labels.get(ins["type"], (ins["type"], "#888"))
        type_label, type_color = type_info

        # Check if expiring soon (within 90 days)
        days_to_expiry = (ins["end_date"] - date.today()).days
        expiry_warning = days_to_expiry <= 90

        st.markdown(f"""
        <div style="background: #1e1e2f; border-left: 4px solid {type_color}; padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <span style="background: {type_color}; color: black; font-size: 10px; padding: 2px 8px; border-radius: 4px;">{type_label}</span>
                    <div style="color: white; font-weight: bold; font-size: 16px; margin-top: 8px;">{ins['name']}</div>
                    <div style="color: #888; font-size: 12px; margin-top: 4px;">Assureur: {ins['insurer']} | Police: {ins['policy_number']}</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: #00d4ff; font-size: 18px; font-weight: bold;">{format_amount(ins['coverage'])}</div>
                    <div style="color: #888; font-size: 12px;">couverture</div>
                    <div style="color: {'#ff6b6b' if expiry_warning else '#00ff88'}; font-size: 12px; margin-top: 4px;">
                        {'Expire dans ' + str(days_to_expiry) + 'j' if expiry_warning else 'Valide'}
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 30px; margin-top: 12px; color: #aaa; font-size: 13px;">
                <div><span style="color: #888;">Prime:</span> {format_amount(ins['premium'])}/an</div>
                <div><span style="color: #888;">Debut:</span> {ins['start_date'].strftime('%d/%m/%Y')}</div>
                <div><span style="color: #888;">Fin:</span> {ins['end_date'].strftime('%d/%m/%Y')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # CDS Section (special for sovereign risk)
    cds_policies = [ins for ins in insurances if ins["type"] == "CDS"]
    if cds_policies:
        st.markdown("### Couverture Risque Souverain (CDS)")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4a1a1a, #1a1a2e); border: 1px solid #ff6b6b; border-radius: 12px; padding: 15px; margin-bottom: 20px;">
            <div style="color: #ff6b6b; font-size: 12px; text-transform: uppercase;">Credit Default Swaps - Protection contre defaut souverain</div>
        </div>
        """, unsafe_allow_html=True)

        for cds in cds_policies:
            spread = cds.get("spread_bps", 0)
            st.markdown(f"""
            <div style="background: #1e1e2f; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <div style="color: white; font-weight: bold;">{cds['name']}</div>
                        <div style="color: #888; font-size: 12px;">Contrepartie: {cds['insurer']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #ff6b6b; font-size: 18px; font-weight: bold;">{spread} bps</div>
                        <div style="color: #888; font-size: 12px;">spread annuel</div>
                    </div>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 20px; color: #aaa; font-size: 13px;">
                    <div>Notionnel: {format_amount(cds['coverage'])}</div>
                    <div>Prime annuelle: {format_amount(cds['premium'])}</div>
                    <div>Maturite: {cds['end_date'].strftime('%d/%m/%Y')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

    # Claims section
    st.markdown("### Historique des Sinistres")

    if claims:
        for claim in claims:
            # Find insurance
            ins = next((i for i in insurances if i["id"] == claim["insurance_id"]), None)
            ins_name = ins["name"] if ins else "N/A"

            status_colors = {"paid": "#00ff88", "pending": "#ffd93d", "rejected": "#ff6b6b"}
            status_labels = {"paid": "Rembourse", "pending": "En cours", "rejected": "Rejete"}

            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
            with col1:
                st.markdown(f"**{claim['type']}**")
                st.caption(f"{claim['date'].strftime('%d/%m/%Y')}")
            with col2:
                st.caption(ins_name)
            with col3:
                st.markdown(f"Demande: {format_amount(claim['amount_claimed'])}")
            with col4:
                if claim["amount_paid"] > 0:
                    st.markdown(f":green[Paye: {format_amount(claim['amount_paid'])}]")
                else:
                    st.caption("En attente")
            with col5:
                color = status_colors.get(claim["status"], "#888")
                label = status_labels.get(claim["status"], claim["status"])
                st.markdown(f"<span style='background: {color}; color: black; padding: 2px 8px; border-radius: 4px; font-size: 11px;'>{label}</span>", unsafe_allow_html=True)
            st.divider()
    else:
        st.info("Aucun sinistre enregistre")

    # Summary
    st.markdown("### Synthese Annuelle")
    col1, col2, col3 = st.columns(3)
    with col1:
        claims_paid = sum(c["amount_paid"] for c in claims if c["status"] == "paid")
        st.metric("Sinistres Rembourses", format_amount(claims_paid))
    with col2:
        ratio = float(claims_paid / total_premiums * 100) if total_premiums > 0 else 0
        st.metric("Ratio S/P", f"{ratio:.1f}%")
    with col3:
        st.metric("Cout Net Assurance", format_amount(total_premiums - claims_paid))


def render_consolidation_tab(data):
    """Consolidated financials"""
    st.markdown("### Bilan Consolide")

    total_assets = sum(s["assets"] for s in data["subsidiaries"])
    treasury = data["accounts"]["principal"]["balance"] + data["accounts"]["tresorerie"]["balance"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Actifs", f"{(total_assets + treasury)/1000000000:.2f}B EUR", "+5.2%")
    with col2:
        st.metric("Fonds Propres", "420M EUR", "+3.1%")
    with col3:
        st.metric("PNB Groupe", "285M EUR", "+8.4%")
    with col4:
        st.metric("Resultat Net", "62M EUR", "+12.3%")

    st.divider()

    st.markdown("### Repartition par Activite")

    activities = [
        {"name": "Banque de detail", "revenue": 180, "percent": 63},
        {"name": "Gestion d'actifs", "revenue": 52, "percent": 18},
        {"name": "Assurance", "revenue": 38, "percent": 13},
        {"name": "Autres", "revenue": 15, "percent": 6},
    ]

    for act in activities:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**{act['name']}**")
            st.caption(f"{act['revenue']}M EUR")
        with col2:
            st.progress(act['percent'] / 100)

    st.divider()

    st.markdown("### Contribution des Filiales")

    for sub in data["subsidiaries"]:
        contribution = float(sub["assets"] / total_assets) * 100
        st.markdown(f"**{sub['name']}** - {contribution:.1f}%")
        st.progress(contribution / 100)


def render_risques_tab(data):
    """Risk management"""
    st.markdown("### Ratios Reglementaires")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ratio CET1", "14.2%", "+0.3%")
        st.caption("Minimum requis: 10.5%")
        st.progress(0.142 / 0.20)
    with col2:
        st.metric("Ratio LCR", "142%", "+5%")
        st.caption("Minimum requis: 100%")
        st.progress(1.42 / 2.0)
    with col3:
        st.metric("Ratio NSFR", "118%", "+2%")
        st.caption("Minimum requis: 100%")
        st.progress(1.18 / 2.0)

    st.divider()

    st.markdown("### Exposition par Type de Risque")

    risks = [
        {"type": "Risque de credit", "exposure": "2.1B EUR", "provision": "45M EUR", "level": "medium"},
        {"type": "Risque de marche", "exposure": "320M EUR", "provision": "8M EUR", "level": "low"},
        {"type": "Risque operationnel", "exposure": "-", "provision": "12M EUR", "level": "low"},
        {"type": "Risque de liquidite", "exposure": "450M EUR", "provision": "-", "level": "low"},
    ]

    for risk in risks:
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            st.markdown(f"**{risk['type']}**")
        with col2:
            st.caption(f"Exposition: {risk['exposure']}")
        with col3:
            st.caption(f"Provision: {risk['provision']}")
        with col4:
            if risk['level'] == 'high':
                st.error("Eleve")
            elif risk['level'] == 'medium':
                st.warning("Moyen")
            else:
                st.success("Faible")

    st.divider()

    st.markdown("### Concentration")

    pool_total = sum(abs(s["pool_balance"]) for s in data["subsidiaries"])
    for sub in data["subsidiaries"]:
        concentration = float(abs(sub["pool_balance"]) / pool_total * 100) if pool_total > 0 else 0.0
        st.markdown(f"{sub['name']}: {concentration:.1f}%")
        st.progress(concentration / 100)


def render_gouvernance_tab(data):
    """Governance"""
    st.markdown("### Conseil d'Administration")

    board = [
        {"name": "Laurent Dubois", "role": "President-Directeur General", "since": "2018"},
        {"name": "Marie-Claire Fontaine", "role": "Directrice Generale Deleguee", "since": "2019"},
        {"name": "Philippe Martin", "role": "Directeur Financier", "since": "2020"},
        {"name": "Isabelle Leroy", "role": "Directrice des Risques", "since": "2021"},
        {"name": "Jean-Pierre Moreau", "role": "Administrateur Independant", "since": "2017"},
    ]

    for member in board:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"**{member['name']}**")
        with col2:
            st.caption(member['role'])
        with col3:
            st.caption(f"Depuis {member['since']}")

    st.divider()

    st.markdown("### Comites")

    committees = [
        {"name": "Comite d'Audit", "members": 4, "meetings": 12},
        {"name": "Comite des Risques", "members": 3, "meetings": 24},
        {"name": "Comite des Remunerations", "members": 3, "meetings": 4},
        {"name": "Comite de Nomination", "members": 2, "meetings": 2},
    ]

    for committee in committees:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"**{committee['name']}**")
        with col2:
            st.caption(f"{committee['members']} membres")
        with col3:
            st.caption(f"{committee['meetings']} reunions/an")

    st.divider()

    st.markdown("### Documents Reglementaires")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Rapport Annuel 2025", "Contenu du rapport annuel...", "rapport_annuel_2025.pdf", mime="application/pdf")
        st.download_button("Rapport Pilier 3", "Contenu du rapport Pilier 3...", "pilier3_2025.pdf", mime="application/pdf")
    with col2:
        st.download_button("Rapport RSE", "Contenu du rapport RSE...", "rse_2025.pdf", mime="application/pdf")
        st.download_button("Charte Ethique", "Contenu de la charte...", "charte_ethique.pdf", mime="application/pdf")
