"""
Login page - Identification bancaire
"""

import streamlit as st


def render_login():
    """Render login page with bank-style authentication"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 40px;
        }
        .step-indicator {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }
        .step {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .step-active {
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            color: white;
        }
        .step-inactive {
            background: #333;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize login state
    if "login_step" not in st.session_state:
        st.session_state.login_step = 1
    if "login_client_id" not in st.session_state:
        st.session_state.login_client_id = ""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" stroke-width="2">
                <rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect>
                <line x1="1" y1="10" x2="23" y2="10"></line>
            </svg>
            <h1 style="background: linear-gradient(90deg, #00d4ff, #7b2cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 16px;">NanoPy Bank</h1>
            <p style="color: #888;">Espace client securise</p>
        </div>
        """, unsafe_allow_html=True)

        # Step indicator
        step1_class = "step-active" if st.session_state.login_step >= 1 else "step-inactive"
        step2_class = "step-active" if st.session_state.login_step >= 2 else "step-inactive"
        st.markdown(f"""
        <div class="step-indicator">
            <div class="step {step1_class}">1</div>
            <div style="width: 60px; height: 2px; background: {'#00d4ff' if st.session_state.login_step >= 2 else '#333'}; align-self: center;"></div>
            <div class="step {step2_class}">2</div>
        </div>
        """, unsafe_allow_html=True)

        # Step 1: Client ID
        if st.session_state.login_step == 1:
            st.markdown("### Etape 1: Identifiant")
            st.markdown("<p style='color: #888; font-size: 14px;'>Saisissez votre identifiant client (8 chiffres)</p>", unsafe_allow_html=True)

            with st.form("login_step1"):
                client_id = st.text_input(
                    "Identifiant client",
                    placeholder="12345678",
                    max_chars=8,
                    help="Votre identifiant a 8 chiffres figure sur votre releve de compte"
                )

                submitted = st.form_submit_button("Continuer", use_container_width=True, type="primary")

                if submitted:
                    if not client_id:
                        st.error("Veuillez saisir votre identifiant")
                    elif len(client_id) != 8 or not client_id.isdigit():
                        st.error("L'identifiant doit contenir 8 chiffres")
                    else:
                        try:
                            from nanopy_bank.core.auth import get_auth_service
                        except ImportError:
                            from ...core.auth import get_auth_service

                        auth = get_auth_service()
                        user = auth.get_user_by_client_id(client_id)

                        if user:
                            st.session_state.login_client_id = client_id
                            st.session_state.login_step = 2
                            st.rerun()
                        else:
                            st.error("Identifiant non reconnu")

        # Step 2: Password
        elif st.session_state.login_step == 2:
            st.markdown("### Etape 2: Mot de passe")
            st.markdown(f"<p style='color: #888; font-size: 14px;'>Identifiant: <strong>{st.session_state.login_client_id}</strong></p>", unsafe_allow_html=True)

            with st.form("login_step2"):
                password = st.text_input(
                    "Mot de passe",
                    type="password",
                    placeholder="••••••••",
                    help="Votre mot de passe personnel"
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("Retour", use_container_width=True):
                        st.session_state.login_step = 1
                        st.rerun()
                with col_b:
                    submitted = st.form_submit_button("Valider", use_container_width=True, type="primary")

                if submitted:
                    if not password:
                        st.error("Veuillez saisir votre mot de passe")
                    else:
                        try:
                            from nanopy_bank.core.auth import get_auth_service
                        except ImportError:
                            from ...core.auth import get_auth_service

                        auth = get_auth_service()
                        session = auth.login_by_client_id(st.session_state.login_client_id, password)

                        if session:
                            user = auth.get_user_by_id(session.user_id)
                            st.session_state.session_id = session.session_id
                            st.session_state.user = user
                            st.session_state.logged_in = True
                            # Reset login state
                            st.session_state.login_step = 1
                            st.session_state.login_client_id = ""
                            st.success(f"Bienvenue {user.display_name}!")
                            st.rerun()
                        else:
                            st.error("Mot de passe incorrect")

            # Reset link
            st.markdown("""
            <div style='text-align: center; margin-top: 10px;'>
                <a href='#' style='color: #00d4ff; font-size: 12px;'>Mot de passe oublie?</a>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        st.markdown("### Comptes demo")
        st.markdown("""
        | Role | Identifiant | Mot de passe |
        |------|-------------|--------------|
        | Client | `10000001` | `demo123` |
        | Conseiller | `20000001` | `demo123` |
        | Directeur | `30000001` | `demo123` |
        | Admin | `40000001` | `demo123` |
        | Holding | `50000001` | `demo123` |
        """)
