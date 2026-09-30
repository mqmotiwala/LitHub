import config as c
import streamlit as st
import utils.css as css


def show_landing():
    css.header(f"{c.APP_NAME} 🤓")
    css.markdown(f"###### Log and reflect on books you've read, all in one place.")

    explanation_text = f"""
    Reading logs end up scattered across notes apps and half-remembered.   
    {c.APP_NAME} keeps the whole picture in one place: what you read, when you read it,
    how you rated it,  
    {css.underline("and the reflections you'd otherwise lose")}.
    """

    css.markdown(f"{explanation_text}")
