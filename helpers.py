import json
import time
import uuid
import humanize
import config as c
import streamlit as st

from datetime import datetime as dt, date

def load_books():
    response = c.s3.get_object(Bucket=c.S3_BUCKET, Key=c.BOOKS_JSON_PATH)
    books_str = response['Body'].read().decode('utf-8')
    books = json.loads(books_str)
    sorted_ids = sort_books(books)
    st.session_state.books = {id: books[id] for id in sorted_ids}

def save_to_s3(obj, path):
    def serializer(obj):
        if isinstance(obj, date):
            return obj.strftime(c.DATE_FORMAT)
        
        raise TypeError(f"Type {type(obj)} not serializable")

    obj_str = json.dumps(obj, indent=4, default=serializer)
    c.s3.put_object(
        Bucket=c.S3_BUCKET,
        Key=path,
        Body=obj_str.encode('utf-8'),
        ContentType='application/json'
    )    

def get_read_count(year=None):
    """
        returns number of books read
        if year is provided, count is retricted to given year
        else, total count is returned
    """
    
    if year is None:
        return len(st.session_state.books)
    
    if not isinstance(year, str):
        try:
            year = str(int(year))
        except:
            raise ValueError("invalid input for year")
    
    cnt = 0
    for id in st.session_state.books:
        if st.session_state.books[id]["end"] is not None and year in st.session_state.books[id]["end"]:
            cnt += 1

    return cnt

def sort_books(books):
    """ 
    sorts books by end date in reverse chronological order (newest first) 
    unread books are at the top of the stack  
    """

    return sorted(
        books, 
        key = lambda k: dt.strptime(books[k]["end"], c.DATE_FORMAT) if books[k]["end"] is not None else dt.now(), 
        reverse = True
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

    st.session_state.GENRES = {
        g
        for book in st.session_state.books.values()
        for g in book["genre"]
    }

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
    quoted_notes = "\n".join(
        f"> {line}" if line.strip() != "" else ">"
        for line in notes.splitlines()
    )

    return quoted_notes

def render_metrics():
    metrics = {
        "Total": get_read_count(),
    }

    for year in range(2020, dt.now().year + 1)[::-1]:
        metrics[f"Read in {year}"] = get_read_count(year)

    with st.container(border=False, horizontal=True, gap="small"):
        for metric, value in metrics.items():
                st.metric(metric, value)

def render_view_mode(id):

    book = st.session_state.books[id]

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
                st.badge(f"_Reading since {humanize.naturaldate(start)} ({get_humanized_timespan(book["start"], dt.now().date())})_", icon=":material/timer_play:", color="orange")

            if book.get("end") is not None:
                st.badge(get_rating_as_stars(book["rating"]), color="yellow")

        st.markdown(format_reflections(book["notes"]))

        with st.container(horizontal=True, horizontal_alignment="left", gap="small"):
            edit = st.button(":material/edit:", key=f"edit-{id}")

            if edit:
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
                st.error("You are missing necessary fields.", icon="🚨")
                return

            data = {
                "title": title,
                "author": author,
                "genre": genre,
                "rating": rating,
                "start": start,
                "end": end,
                "notes": notes, 
            }
            
            st.session_state.books[id] = data

            # update s3
            save_to_s3(st.session_state.books, c.BOOKS_JSON_PATH)
            load_books()

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

def render_reading_list():
    response = c.s3.get_object(Bucket=c.S3_BUCKET, Key=c.READING_LIST_JSON_PATH)
    reading_list_str = response['Body'].read().decode('utf-8')
    reading_list = json.loads(reading_list_str)

    reading_list = sorted(
        reading_list, 
        key = lambda book: dt.strptime(book["added_on"], c.DATE_FORMAT), 
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
                if not all(s and s.strip() for s in [title, author, genre]):
                    st.error("You are missing necessary fields.", icon="🚨")
                else:
                    reading_list.append({
                        "title": title,
                        "author": author,
                        "notes": notes,
                        "added_on": dt.now().strftime(c.DATE_FORMAT),
                    })

                    save_to_s3(reading_list, c.READING_LIST_JSON_PATH)
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

                st.badge(f"Added on {book['added_on']}", icon=":material/today:")

                if book.get("notes"):
                    st.markdown(format_reflections(book["notes"]))

                if st.button(":material/delete:", key=f"remove-{i}"):
                    del reading_list[i]
                    save_to_s3(reading_list, c.READING_LIST_JSON_PATH)
                    st.rerun()
