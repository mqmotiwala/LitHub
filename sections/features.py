import humanize
import config as c
import helpers as h
import streamlit as st
import utils.css as css

from datetime import datetime as dt

# Landing-only demo content.
DEMO_BOOK = {
    "title": "Project Hail Mary",
    "author": "Andy Weir",
    "genre": ["Science Fiction", "Space Opera"],
    "rating": 5,
    "start": "2026-03-02",
    "end": "2026-03-19",
    # triple-quoted for the real line breaks. The ">" on the Notable Quotes line
    # survives format_reflections(), which prefixes every line with "> ", so that
    # line lands as a nested blockquote inside the reflections quote block.
    "notes": """As awkward as Andy's writing is at times, its also so much fun seeing him ground some science fiction elements with real-life engineering & scientific explanations for observed behavior.

  
Rocky steals the whole book.  
Stayed up far too late on a work night for the last hundred pages.  

**Notable Quotes**
> Do you believe in God? [...] I think He was pretty awesome to make relativity a thing, don't you? The faster you go, the less time you experience.  
It's like He's inviting us to explore the universe, you know?""",
}

DEMO_READ_METRICS = {"Total Read": 33, "2026": 10, "2025": 11, "2024": 12}
DEMO_RATING_METRICS = {"Average Rating": "4.18", "★★★★★": 14, "★★★★☆": 11, "★★★☆☆": 8}
DEMO_GENRE_METRICS = [("Science Fiction", 13, "39%"), ("Philosophy", 10, "30%"), ("Literature", 8, "24%"), ("Non-Fiction", 2, "6%")]

DEMO_READING_LIST = [
    ("Moth Smoke", "Mohsin Hamid", ["Fiction"], "Mar 04 2026", "> Zahra recommended this.  \nAbout 2 friends struggling to connect due to taking different life paths"),
    ("Fahrenheit 451", "Ray Bradbury", ["Science Fiction"], "Sep 29 2025", "> explores how censorship and technology can erode curiosity and critical thinking."),
]


def _show_demo_book():
    """mirrors the real book card, so the landing shows the actual look of the app"""

    with st.container(border=True):
        with st.container(gap=None):
            st.header(DEMO_BOOK["title"])
            st.markdown(f"_{DEMO_BOOK["author"]}_")

        with st.container(horizontal=True, horizontal_alignment="left", gap=None):
            st.badge(f"_{', '.join(DEMO_BOOK["genre"])}_", icon=":material/menu_book:", color="green")

            start = dt.strptime(DEMO_BOOK["start"], c.DATE_FORMAT)
            end = dt.strptime(DEMO_BOOK["end"], c.DATE_FORMAT)
            timespan = h.get_humanized_timespan(DEMO_BOOK["start"], DEMO_BOOK["end"])
            st.badge(f"_{humanize.naturaldate(start)} -> {humanize.naturaldate(end)} ({timespan})_", icon=":material/timeline:")

            st.badge(h.get_rating_as_stars(DEMO_BOOK["rating"]), color="yellow")

        st.markdown(h.format_reflections(DEMO_BOOK["notes"]))


def _show_demo_metrics(metrics):
    """one row of metrics, laid out the same way the real analytics panel does it"""

    with st.container(border=False, horizontal=True, gap="small", horizontal_alignment="center", vertical_alignment="top"):
        for metric, value in metrics.items():
            st.metric(metric, value)


def show_features():
    css.divider()

    with st.container():
        css.header("Reflect on the books you read", lvl=5, underline_text=False)
        _show_demo_book()

    css.empty_space()

    with st.container():
        css.header("Get insights into your reading habits", lvl=5, underline_text=False)
        with st.expander("Analytics", icon=":material/analytics:", expanded=True):
            _show_demo_metrics(DEMO_READ_METRICS)
            st.divider()
            _show_demo_metrics(DEMO_RATING_METRICS)
            st.divider()
            with st.container(border=False, horizontal=True, gap="small", horizontal_alignment="center", vertical_alignment="top"):
                for genre, count, share in DEMO_GENRE_METRICS:
                    st.metric(genre, count, delta=share, delta_color="off")

    css.empty_space()

    with st.container():
        css.header("Keep an organized reading list", lvl=5, underline_text=False)

        for title, author, genre, added_date, notes in DEMO_READING_LIST:
            with st.container(border=True):
                with st.container(gap=None):
                    st.header(title)
                    st.markdown(f"_{author}_")

                with st.container(horizontal=True, horizontal_alignment="left", gap=None):
                    st.badge(f"_{', '.join(genre)}_", icon=":material/menu_book:", color="green")
                    st.badge(f"Added {added_date}", icon=":material/today:")

                    st.markdown(notes)
