import config as c
import utils.auth as a
import streamlit as st


def show_header():
    """
    Top of the authenticated app. Logout gets its own row, tucked into the top
    right corner, so the title below keeps the full width it had before auth.
    """

    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("Logout", key=c.LOGOUT_BUTTON_KEY_NAME):
            a.logout()

    st.header(f"{c.APP_NAME}: {st.session_state.user.get_display_name()}'s Reading Log 🤓")
