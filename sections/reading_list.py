import humanize
import config as c
import helpers as h
import streamlit as st

from datetime import datetime as dt
from utils.logger import log_event


def show_reading_list():
    reading_list = h.load_from_s3(st.session_state.user.READING_LIST_JSON_PATH, default=[])

    reading_list = sorted(
        reading_list, 
        key = lambda book: dt.strptime(book["added_on"], c.DATETIME_FORMAT), 
        reverse = True
    )

    with st.expander(":material/book_5: Add to reading list", expanded=False):
        with st.form("add-reading-list-form", clear_on_submit=True, border=False):
            cols = st.columns(3)

            with cols[0]:
                title = st.text_input("Title", placeholder="Book title", max_chars=50)

            with cols[1]:
                author = st.text_input("Author", placeholder="Book author", max_chars=50)

            with cols[2]:
                genre = st.multiselect("Genre", sorted(st.session_state.GENRES), max_selections=3, accept_new_options=True)

            notes = st.text_area("Notes", placeholder=c.TEXT_INPUT_PLACEHOLDER)

            if st.form_submit_button("Add"):
                if not all(s and s.strip() for s in [title, author] + genre):
                    log_event("reading_list_add_rejected", st.session_state.user, level="warning", title=title)
                    st.error("You are missing necessary fields.", icon="🚨")
                else:
                    reading_list.append({
                        "title": title,
                        "author": author,
                        "notes": notes,
                        "genre": genre, 
                        "added_on": dt.now().strftime(c.DATETIME_FORMAT),
                    })

                    h.save_to_s3(reading_list, st.session_state.user.READING_LIST_JSON_PATH)
                    log_event("reading_list_added", st.session_state.user, title=title, author=author)
                    st.rerun()

    if not reading_list:
        st.info("No books in your reading list yet.")
        return

    # Show reading list
    search_txt = st.text_input("filter reading list", label_visibility="collapsed", icon=":material/search:", placeholder=c.SEARCH_BAR_PLACEHOLDER)
    for i, book in enumerate(reading_list):
        if search_txt is None or any(search_txt in str(value).lower() for value in book.values()):
            with st.container(border=True):
                with st.container(gap=None):
                    st.header(book["title"])
                    st.markdown(f"_{book["author"]}_")

                with st.container(horizontal=True, horizontal_alignment="left", gap=None):
                    st.badge(f"_{', '.join(book["genre"])}_", icon=":material/menu_book:", color="green")

                    start = dt.strptime(book["added_on"], c.DATETIME_FORMAT) 
                    st.badge(f"Added {humanize.naturaldate(start)}", icon=":material/today:")

                if book.get("notes"):
                    st.markdown(h.format_reflections(book["notes"]))

                if st.button(":material/delete:", key=f"remove-{i}"):
                    del reading_list[i]
                    h.save_to_s3(reading_list, st.session_state.user.READING_LIST_JSON_PATH)
                    log_event("reading_list_removed", st.session_state.user, title=book["title"])
                    st.rerun()
