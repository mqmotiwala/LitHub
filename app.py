import config as c
import helpers as h
import streamlit as st

st.header("LitHub: Mufi's Reading Log 🤓")

h.initialize_app()
h.render_metrics()

tabs = st.tabs(["LitHub", "Reading List"])
with tabs[0]:
    with st.expander(":material/book_5: Add a new book", expanded=False):
        h.render_edit_mode()

    search_txt = st.text_input("filter books", label_visibility="collapsed", icon=":material/search:", placeholder=c.SEARCH_BAR_PLACEHOLDER)
    for id in st.session_state.books:
        if id in st.session_state.edit_mode:
            h.render_edit_mode(id)
        else:
            if search_txt is None or any(search_txt in str(value).lower() for value in st.session_state.books[id].values()):
                h.render_view_mode(id)

with tabs[1]:
    h.render_reading_list()