from pathlib import Path
from typing import Protocol

import numpy as np
import streamlit as st
from PIL import Image

from src.database import query_database
from src.image import CellImageMeta


def return_selectbox_result(lst):
    return lst if lst is not None else []


class Renderer(Protocol):
    def render(self):
        ...


class TitleRenderer:
    def __init__(self, title: str):
        self.title = title

    def render(self):
        st.title(self.title)


class OptionRenderer:
    def __init__(self, title: str, value):
        self.title = title
        self.value = value

    def render(self):
        return st.checkbox(self.title, value=self.value)


class LabelProgressRenderer:
    def __init__(self, project_name):
        self.project_name = project_name
        self.total_cell_count = self.get_total_cell_count()
        self.total_labelled_cell_count = self.get_labelled_cell_count()

    def get_total_cell_count(self) -> int:
        return query_database(f"SELECT COUNT(*) FROM {self.project_name}_cell")[
            0
        ].get("COUNT(*)")

    def get_labelled_cell_count(self) -> int:
        return query_database(
            f"SELECT count(distinct(i.cell_id)) as cell_count FROM {self.project_name}_image_quality q LEFT JOIN {self.project_name}_image i ON q.image_id = i.image_id"
        )[0].get("cell_count")

    def render(self):
        st.write("The number of labeled cell:", self.total_labelled_cell_count)
        st.write(
            "The number of unlabeled cell:",
            self.total_cell_count - self.total_labelled_cell_count,
        )
        st.write(
            f"Progress: {self.total_labelled_cell_count / self.total_cell_count * 100:.0f}%"
        )
        st.progress(self.total_labelled_cell_count / self.total_cell_count)
