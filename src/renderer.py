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


class CellImageRenderer:
    def __init__(self, image_path: Path):
        self.image_path = image_path
        self.image = self.open_image()

    def open_image(self):
        image = Image.open(self.image_path)
        image_arr = np.array(image)

        if image_arr.min() > 255:
            return self._normalize_image(image_arr)
        return image

    def _normalize_image(self, image_arr) -> Image:
        return Image.fromarray(
            np.round(
                (image_arr - image_arr.min())
                / (image_arr.max() - image_arr.min())
                * 255
            ).astype(np.uint8)
        )  # type: ignore

    def render(self, width):
        st.image(self.image, width=width)


class ImageQualityRenderer:
    __QualityRenderer = None

    def __init__(self, project_name: str, cellimage_list: list[CellImageMeta]):
        self.project_name = project_name
        self.cellimage_list = cellimage_list

    def get_default_quality(self):
        results = [
            query_database(
                f"SELECT quality FROM {self.project_name}_image_quality WHERE image_id = {self.image_id}"
            )
            for image_id in image_ids
        ]

        if len(results) == 1:
            if len(results[0]) == 0:
                return None
            elif results[0][0].get("quality", None) == 0:
                return "Good"
            elif results[0][0].get("quality", None) == 1:
                return "Bad"  # type: ignore

        elif len(results) == 2:
            if len(results[1]) == 0:
                return None

            if len(results[0]) == 0:
                return None

            elif (results[0][0].get("quality", None) == 0) and (
                results[1][0].get("quality", None) == 0
            ):
                return "Good"
            elif (results[0][0].get("quality", None) == 1) and (
                results[1][0].get("quality", None) == 1
            ):
                return "Bad"
            elif results[0][0].get("quality", None) != results[1][0].get(
                "quality", None
            ):
                return None

    def render(self):
        self.__QualityRenderer.render()


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
