import json
import uuid
import humanize
import config as c
import streamlit as st

from datetime import datetime as dt, date

def load_books():
    response = c.s3.get_object(Bucket=c.S3_BUCKET, Key=c.BOOKS_JSON_PATH)
    books_str = response['Body'].read().decode('utf-8')
    st.session_state.books = json.loads(books_str)

def save_books():
    def serializer(obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        
        raise TypeError(f"Type {type(obj)} not serializable")

    books_str = json.dumps(st.session_state.books, indent=4, default=serializer)
    c.s3.put_object(
        Bucket=c.S3_BUCKET,
        Key=c.BOOKS_JSON_PATH,
        Body=books_str.encode('utf-8'),
        ContentType='application/json'
    )

def initialize_app():
    st.set_page_config(
        page_title=c.APP_NAME, 
        page_icon=":material/local_library:", 
        layout="centered"
    )

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = set()

    if "books" not in st.session_state:
        load_books()

def get_rating_as_stars(rating):
    if rating is None:
        rating = 0
    
    if isinstance(rating, float):
        rating = int(rating)

    return f"{c.FILLED_STAR*rating}{c.EMPTY_STAR*(c.MAX_RATING-rating)}"

def get_humanized_timespan(start, end):
    if start == end:
        return "less than a day"
    
    ensure_dt = lambda v: dt.strptime(v, c.DATE_FORMAT).date() if isinstance(v, str) else v
    start, end = ensure_dt(start), ensure_dt(end)

    return humanize.precisedelta(end - start)

def format_reflections(notes):
    parts = notes.split("\n")

    return "> " + parts[0] + "\n > ".join(parts[1:])

def render_view_mode(book):
    with st.container(border=True):
        with st.container(gap=None):
            st.header(book["title"])
            st.markdown(f"_{book["author"]}_")

        with st.container(horizontal=True, horizontal_alignment="left", gap=None):
            st.badge(f"_{', '.join(book["genre"])}_", icon=":material/menu_book:", color="green")

            start = dt.strptime(book["start"], c.DATE_FORMAT)
            if book.get("end"):
                end = dt.strptime(book["end"], c.DATE_FORMAT)
                st.badge(f"_{humanize.naturaldate(start)} -> {humanize.naturaldate(end)} ({get_humanized_timespan(book["start"], book["end"])})_", icon=":material/timeline:")
            else:
                st.badge(f"_Reading since {humanize.naturaldate(start)} ({get_humanized_timespan(book["start"], dt.now().date())})_", icon=":material/timer_play:")

            st.badge(get_rating_as_stars(book["rating"]), color="yellow")

        st.markdown(format_reflections(book["notes"]))

        with st.container(horizontal=True, horizontal_alignment="left", gap="small"):
            edit = st.button(":material/edit:", key=f"edit-{book["id"]}")

            if edit:
                st.session_state.edit_mode.add(book["id"])
                st.rerun()

def render_edit_mode(book={}):
    """
        this is used to render the edit form for existing books, or when creating new 
    """

    # show border is used to toggle border, 
    # by default it's shown but within the new book expander we turn it off
    show_border = True if len(book) != 0 else False 

    # get id, or generate one for new books
    id = book.get("id", str(uuid.uuid4()))
    with st.form(f"form-{id}", border=show_border):
        cols = st.columns(2)
        
        with cols[0]:
            title = st.text_input("Title", value=book.get("title"), max_chars=50, placeholder=c.TEXT_INPUT_PLACEHOLDER)
            start = st.date_input("Start Date", value=book.get("start"), format="YYYY-MM-DD")
            rating = st.number_input("Rating", min_value=0, max_value=5, value=book.get("rating", c.MIN_RATING), step=1)

        with cols[1]:
            author = st.text_input("Author", value=book.get("author"), max_chars=50, placeholder=c.TEXT_INPUT_PLACEHOLDER)
            end = st.date_input("End Date", value=book.get("end"), format="YYYY-MM-DD")
            genre = st.multiselect("Genre", sorted(c.GENRES), max_selections=3, accept_new_options=True, default=book.get("genre"))

        notes = st.text_area("Reflections", value=book.get("notes"), height="content", placeholder=c.TEXT_INPUT_PLACEHOLDER)

        if st.form_submit_button("Save", key=f"save-{id}"):
            if not all(s and s.strip() for s in [title, author]) or start is None or len(genre) == 0:
                st.error("You are missing necessary fields.", icon="🚨")
            else:
                data = {
                    "id": id,
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "rating": rating,
                    "start": start,
                    "end": end,
                    "notes": notes, 
                }

                # since this function can be called to edit existing books, or create new ones
                # we check to see if the book being edited already exists in books.json 
                # if it does, we find the index and update the contents there
                # else, we append new data to books arr
                idx = None
                for i, b in enumerate(st.session_state.books):
                    if id == b["id"]:
                        idx = i
                        break

                if idx is not None:
                    st.session_state.books[idx] = data
                else:            
                    st.session_state.books.append(data)

                # update s3
                save_books()
                load_books()

                # reset edit mode view
                # discard doesn't raise an error if id doesn't exist in set
                st.session_state.edit_mode.discard(id)
                st.rerun()
