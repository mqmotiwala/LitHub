import json
import humanize
import config as c
import streamlit as st

from datetime import datetime as dt, date

def load_from_s3(path, default):
    """
        reads and parses a JSON object from S3
        a user who has just registered owns no objects yet, so a missing key
        returns the supplied default instead of raising
    """

    try:
        response = c.s3.get_object(Bucket=c.S3_BUCKET, Key=path)
    except c.s3.exceptions.NoSuchKey:
        return default

    return json.loads(response['Body'].read().decode('utf-8'))

def load_books():
    books = load_from_s3(st.session_state.user.BOOKS_JSON_PATH, default={})
    sorted_ids = sort_books(books)

    st.session_state.books = {id: books[id] for id in sorted_ids}
    
    # generate book counts for handling duplicate titles in anchors
    st.session_state.book_counts = {}
    for id in st.session_state.books:
        st.session_state.book_counts[st.session_state.books[id]["title"]] = st.session_state.book_counts.get(st.session_state.books[id]["title"], 0) + 1

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
        return len([book for book in st.session_state.books.values() if book.get("end") is not None])
    
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

def get_earliest_read_year():
    """
        returns the year of the earliest finished book
        falls back to the current year for a user with nothing finished yet
    """

    end_years = [
        int(book["end"][:4])
        for book in st.session_state.books.values()
        if book.get("end") is not None
    ]

    return min(end_years) if end_years else dt.now().year

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
    """
        per-session setup for an authenticated user
    """

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
