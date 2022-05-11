from collections import OrderedDict

import streamlit as st

import src.center_labeller_page as center_labeller_page
import src.labelled_page as labelled_page
import src.quality_labeller_page as quality_labeller_page

# TODO: downloader inject to each page


def main():
    pages = OrderedDict(
        {
            "quality_labeller_page": quality_labeller_page.app,
            "center_labeller_page": center_labeller_page.app,
            "labelled_page": labelled_page.app,
        }
    )
    with st.sidebar:
        st.radio(
            "App Navigation",
            list(pages.keys()),
            key="page",
        )

    pages[st.session_state.page]()


if __name__ == "__main__":
    main()
