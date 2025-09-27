import helpers as h
import streamlit as st

st.title("LitHub -- Mufi's Reading Log 🤓")

h.initialize_app()
h.render_metrics()

tabs = st.tabs(["LitHub", "Reading List"])
with tabs[0]:
    with st.expander(":material/book_5: Add a new book", expanded=False):
        h.render_edit_mode()

    for id in st.session_state.books:
        if id in st.session_state.edit_mode:
            h.render_edit_mode(id)
        else:
            h.render_view_mode(id)

with tabs[1]:
    h.render_reading_list()