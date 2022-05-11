import streamlit as st


def set_session_state(*args):
    for arg in args:
        if arg not in st.session_state:
            st.session_state[arg] = None
