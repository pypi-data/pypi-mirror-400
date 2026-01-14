import os

import extra_streamlit_components as stx
import streamlit as st
from dotenv import find_dotenv, load_dotenv


def setup_authentication(cfg):
    """Setup authentication for the app using session state and cookies."""
    # Load environment variables
    load_dotenv(find_dotenv(usecwd=True))

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Check cookie
    cookie_manager = stx.CookieManager()
    auth_cookie = cookie_manager.get("auth_cookie")
    if auth_cookie == "authenticated":
        st.session_state.authenticated = True

    # Determine if authentication is required
    require_auth = cfg.get("auth", False) if cfg else False

    # Get passcode from environment
    passcode_from_env = os.getenv("PASSCODE")

    # Need authentication and not authenticated yet
    if require_auth and not st.session_state.authenticated:
        st.markdown("### Login")
        passcode = st.text_input("Enter Passcode", type="password")

        if passcode and passcode_from_env:
            if passcode == passcode_from_env:
                st.session_state.authenticated = True
                cookie_manager.set(
                    "auth_cookie", "authenticated", max_age=30 * 24 * 60 * 60
                )
                st.rerun()
            else:
                st.error("Invalid passcode")
                st.session_state.authenticated = False
        elif passcode and not passcode_from_env:
            st.error(
                "No passcode configured. Please set PASSCODE environment variable."
            )

        # Stop execution if not authenticated
        if not st.session_state.authenticated:
            st.stop()
