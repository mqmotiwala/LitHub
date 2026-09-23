import config as c
import helpers as h
import streamlit as st

from datetime import datetime as dt


def show_analytics():
    with st.expander("Analytics", icon=":material/analytics:"):
        total = h.get_read_count()

        # nothing finished yet means every metric below is either zero or a
        # division by zero, so prompt instead of rendering an empty panel
        if total == 0:
            st.markdown("Start documenting your read history to get analytics.")
            return

        with st.container(border=False, gap=None):
            # reading metrics 
            metrics = {
                "Total Read": total,
            }

            # start the year breakdown at the user's first finished book, so a new
            # user isn't shown a row of zeros for years before they joined
            for year in range(h.get_earliest_read_year(), dt.now().year + 1)[::-1]:
                metrics[f"{year}"] = h.get_read_count(year)

            with st.container(border=False, horizontal=True, gap="small", horizontal_alignment="center", vertical_alignment="top"):
                for metric, value in metrics.items():
                        st.metric(metric, value)

            st.divider()

            # ratings metrics
            ratings = [book["rating"] for book in st.session_state.books.values() if book.get("end") is not None]
            metrics = {
                "Average Rating": f"{sum(ratings)/len(ratings):.2f}",
            }

            for i in range(c.MAX_RATING, c.MIN_RATING - 1, -1):
                star_str = lambda n: n*c.FILLED_STAR + (c.MAX_RATING-n)*c.EMPTY_STAR
                metrics[star_str(i)] = sum([1 for rating in ratings if i == rating])

            with st.container(border=False, horizontal=True, gap="small", horizontal_alignment="center", vertical_alignment="top"):
                for metric, value in metrics.items():
                        st.metric(metric, value)

            st.divider()

            # genre metrics
            genre_counts = {}
            for book in st.session_state.books.values():
                if book.get("end") is not None:
                    for g in book["genre"]:
                        genre_counts[g] = genre_counts.get(g, 0) + 1

            sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
            with st.container(border=False, horizontal=True, gap="small", horizontal_alignment="center", vertical_alignment="top"):
                for genre, count in sorted_genres[:7]:
                    st.metric(genre, count, delta=f"{count/total*100:.0f}%", delta_color="off")
