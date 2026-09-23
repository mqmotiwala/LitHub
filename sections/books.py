import re
import uuid
import humanize
import config as c
import helpers as h
import streamlit as st

from datetime import datetime as dt
from utils.logger import log_event


def render_view_mode(id):

    book = st.session_state.books[id]

    with st.container(border=True):
        with st.container(gap=None):
            # specify anchors so we can link to specific books
            # without anchors, the same book title would create duplicate anchors
            # to keep URLs short, we append part of the uuid for a unique anchor only when needed
            slugify = lambda s: re.sub(r'[^a-zA-Z0-9\-]', '', s.replace(' ', '-')).lower()

            anchor = slugify(book["title"])
            anchor += f"-{id[:4]}" if st.session_state.book_counts[book["title"]] > 1 else ""

            st.header(book["title"], anchor=anchor)
            st.markdown(f"_{book["author"]}_")

        with st.container(horizontal=True, horizontal_alignment="left", gap=None):
            st.badge(f"_{', '.join(book["genre"])}_", icon=":material/menu_book:", color="green")

            start = dt.strptime(book["start"], c.DATE_FORMAT)
            if book.get("end"):
                end = dt.strptime(book["end"], c.DATE_FORMAT)
                st.badge(f"_{humanize.naturaldate(start)} -> {humanize.naturaldate(end)} ({h.get_humanized_timespan(book["start"], book["end"])})_", icon=":material/timeline:")
            else:
                st.badge(f"_Reading since {humanize.naturaldate(start)} ({h.get_humanized_timespan(book["start"], dt.now().date())})_", icon=":material/timer_play:", color="orange")

            if book.get("end") is not None:
                st.badge(h.get_rating_as_stars(book["rating"]), color="yellow")

        st.markdown(h.format_reflections(book["notes"]))

        with st.container(horizontal=True, horizontal_alignment="left", gap="small"):
            edit = st.button(":material/edit:", key=f"edit-{id}")

            if edit:
                log_event("book_edit_opened", st.session_state.user, title=book["title"])
                st.session_state.edit_mode.add(id)
                st.rerun()

def render_edit_mode(id=None):
    """
        this is used to render the edit form for existing books, or when creating new 
    """

    # generate an id for new books
    # save generated id to session_state to prevent forgetting during re-runs
    # that introduces a sneaky bug where new books can not be logged
    if id is None:
        if "new_form_id" not in st.session_state:
            id = str(uuid.uuid4())
            st.session_state.new_form_id = id
        else:
            id = st.session_state.new_form_id    

    # show border is used to toggle border, 
    # by default it's shown but within the new book expander we turn it off
    book = st.session_state.books.get(id, {})
    show_border = True if len(book) != 0 else False 

    # an empty book dict means this form is creating rather than editing;
    # captured before the save branch so the logged event is accurate
    is_new_book = len(book) == 0

    # get id, or generate one for new books
    with st.form(f"form-{id}", border=show_border):
        cols = st.columns(2)
        
        with cols[0]:
            title = st.text_input("Title", value=book.get("title"), max_chars=50, placeholder=c.TEXT_INPUT_PLACEHOLDER)
            start = st.date_input("Start Date", value=book.get("start"), format="YYYY-MM-DD")
            rating = st.number_input("Rating", min_value=0, max_value=5, value=book.get("rating", c.MIN_RATING), step=1)

        with cols[1]:
            author = st.text_input("Author", value=book.get("author"), max_chars=50, placeholder=c.TEXT_INPUT_PLACEHOLDER)
            end = st.date_input("End Date", value=book.get("end"), format="YYYY-MM-DD")
            genre = st.multiselect("Genre", sorted(st.session_state.GENRES), max_selections=3, accept_new_options=True, default=book.get("genre"))

        notes = st.text_area("Reflections", value=book.get("notes"), height="content", placeholder=c.TEXT_INPUT_PLACEHOLDER)
        notes = "" if notes is None else notes

        if st.form_submit_button("Save", key=f"save-{id}"):
            if not all(s and s.strip() for s in [title, author]) or start is None or len(genre) == 0:
                log_event("book_save_rejected", st.session_state.user, level="warning", is_new=is_new_book, title=title)
                st.error("You are missing necessary fields.", icon="🚨")
                return

            data = {
                "title": title,
                "author": author,
                "genre": genre,
                "rating": rating,
                "rating_string": rating*c.FILLED_STAR + (c.MAX_RATING - rating)*c.EMPTY_STAR,
                "start": start,
                "end": end,
                "notes": notes, 
            }
            
            st.session_state.books[id] = data

            # update s3
            h.save_to_s3(st.session_state.books, st.session_state.user.BOOKS_JSON_PATH)
            h.load_books()

            log_event(
                "book_added" if is_new_book else "book_updated",
                st.session_state.user,
                title=title,
                author=author,
                rating=rating,
                finished=end is not None,
            )

            # reset edit mode view
            # discard doesn't raise an error if id doesn't exist in set
            st.session_state.edit_mode.discard(id)

            # if a new book was being added, we can now reset the form by deleting its id
            # the consequence of this is that if:
            # (1) a new book was being added, 
            # (2) then an existing book was edited and saved
            # then, the new book form would get reset still
            # this is an acceptable side effect
            st.session_state.pop("new_form_id", None) # safely passes if key not found

            st.rerun()

def show_books():
    """the reading log tab: add-new form, search, then a card per book"""

    with st.expander(":material/book_5: Add a new book", expanded=False):
        render_edit_mode()

    search_txt = st.text_input("filter books", label_visibility="collapsed", icon=":material/search:", placeholder=c.SEARCH_BAR_PLACEHOLDER)
    for id in st.session_state.books:
        if id in st.session_state.edit_mode:
            render_edit_mode(id)
        else:
            if search_txt is None or any(search_txt in str(value).lower() for value in st.session_state.books[id].values()):
                render_view_mode(id)
