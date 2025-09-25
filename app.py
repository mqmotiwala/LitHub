import helpers as h
import streamlit as st

h.initialize_app()

st.title("Mufaddal's LitHub")

st.write(len(st.session_state.books))

with st.expander(":material/book_5: Add a new book", expanded=False):
    h.render_edit_mode()
        
for book in st.session_state.books:
    if book["id"] in st.session_state.edit_mode:
        h.render_edit_mode(book)
    else:
        h.render_view_mode(book)