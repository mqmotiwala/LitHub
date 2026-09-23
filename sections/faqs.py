import config as c
import streamlit as st
import utils.css as css


def show_faqs():
    css.divider()
    st.subheader("💡 Frequently Asked Questions")

    sec1, sec2 = st.columns([1, 2])
    with sec1:
        css.markdown(f"Have another question? Send me an [{css.highlight("email")}](mailto:mqmotiwala@gmail.com).")

    with sec2:
        with st.expander(f"What is {c.APP_NAME}?"):
            answer = f"""
                A simplified reading log.  
                You add a book, rate it, and write down what you thought.
                {c.APP_NAME} keeps the history and turns it into analytics over time.

                It is deliberately not a social network.  
                There are no feeds, no followers, and nothing to write for an audience.
            """
            st.write(answer)

        with st.expander("Who can see my books?"):
            answer = f"""
                Only you.  
                
                {c.APP_NAME} gives you your own private log, and every book,
                reflection, and reading list entry is accessible by you alone.
            """
            css.markdown(answer)

        with st.expander("Is it free?"):
            answer = f"""
                Yes. {c.APP_NAME} is free, and there will never be a paid tier to upsell you to.
            """
            st.write(answer)

    css.empty_space()
