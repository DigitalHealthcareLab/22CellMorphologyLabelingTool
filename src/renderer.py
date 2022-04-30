from pathlib import Path
from typing import Protocol

import numpy as np
import streamlit as st
from PIL import Image

from src.database import query_database
from src.image import CellImage


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


class ProjectListRenderer:
    def __init__(self):
        self.project_list = self.get_project_list()

    def get_project_list(self):
        """Get project list based on mysql tables in tomocube database"""

        data_list = query_database(
            """SELECT TABLE_NAME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = 'tomocube'
            AND TABLE_NAME LIKE '%patient'"""
        )
        return [
            data["TABLE_NAME"].replace("_patient", "") for data in data_list  # type: ignore
        ]

    def render(self):
        if len(self.project_list) == 0:
            return st.selectbox("Tomocube project", ["Not Avaliable"])
        return st.selectbox("Tomocube project", self.project_list)


class PatientListRenderer:
    def __init__(self, project_name):
        self.project_name = project_name
        self.data_list = self.get_datalist()

    def get_datalist(self):
        data_list = query_database(
            f"SELECT patient_id FROM {self.project_name}_patient"
        )
        return [data["patient_id"] for data in data_list]  # type: ignore

    def render(self):
        return st.selectbox("Patient ID", self.data_list, index=0)


class CellTypeRenderer:
    def __init__(self, project_name, patient_id):
        self.project_name = project_name
        self.patient_id = patient_id
        self.celltype_list = self.get_celltype_list()

    def get_celltype_list(self):
        sql = f"""SELECT distinct(cell_type) FROM {self.project_name}_cell WHERE patient_id = {self.patient_id} ORDER BY cell_type"""

        return [data["cell_type"] for data in query_database(sql)]  # type: ignore

    def render(self):
        if self.celltype_list is not None:
            return st.selectbox("Cell type", self.celltype_list, index=0)
        else:
            return st.selectbox("Cell type", ["Not Available"])


class FilterCellTypeRenderer(CellTypeRenderer):
    def get_celltype_list(self):
        sql = f"""SELECT distinct(cell_type) 
                FROM {self.project_name}_cell 
                WHERE patient_id = {self.patient_id} 
                AND cell_id IN 
                    (SELECT distinct(cell_id) 
                    FROM {self.project_name}_image 
                    WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_quality)) 
                ORDER BY cell_type"""

        return [data["cell_type"] for data in query_database(sql)]  # type: ignore


class CellNumberRenderer:
    def __init__(self, project_name, patient_id, cell_type):
        self.project_name = project_name
        self.patient_id = patient_id
        self.cell_type = cell_type
        self.cellnumber_list = (
            None if self.cell_type is None else self.get_cellnumber_list()
        )

    def get_cellnumber_list(self):
        sql = f"""SELECT cell_number 
                FROM {self.project_name}_cell 
                WHERE cell_type = '{self.cell_type}' 
                AND patient_id = {self.patient_id} 
                ORDER BY cell_number"""

        return [data["cell_number"] for data in query_database(sql)]  # type: ignore

    def render(self):
        if self.cellnumber_list is not None:
            return st.selectbox("Cell number", self.cellnumber_list, index=0)
        else:
            return st.selectbox("Cell number", [])


class FilterCellNumberRenderer(CellNumberRenderer):
    def get_cellnumber_list(self):
        sql = f"""SELECT distinct(cell_number) 
                FROM {self.project_name}_cell 
                WHERE cell_type = '{self.cell_type}' 
                AND patient_id = {self.patient_id} 
                AND cell_id IN 
                    (SELECT distinct(cell_id) FROM {self.project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_quality)) 
                ORDER BY cell_number"""

        return [data["cell_number"] for data in query_database(sql)]  # type: ignore


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

    def __init__(self, project_name: str, cellimage_list: list[CellImage]):
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
