import config as c
import helpers as h
import utils.auth as a
import streamlit as st

from sections.faqs import show_faqs
from sections.books import show_books
from sections.header import show_header
from sections.landing import show_landing
from sections.features import show_features
from sections.analytics import show_analytics
from sections.reading_list import show_reading_list

st.set_page_config(
    page_title=c.APP_NAME,
    page_icon=c.APP_ICON,
    layout="centered"
)
if not st.user.is_logged_in:
    show_landing()
    a.login_button(unique_key="login_top")
    show_features()
    show_faqs()
    a.login_button(unique_key="login_bottom")
    st.stop()

a.ensure_user_loaded()

show_header()

h.initialize_app()
show_analytics()

tabs = st.tabs(["LitHub", "Reading List"])
with tabs[0]:
    show_books()

with tabs[1]:
    show_reading_list()
