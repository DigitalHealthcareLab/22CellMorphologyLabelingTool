import logging
from sqlite3 import sqlite_version_info

import streamlit as st

from src.database import query_database
from src.renderer import return_selectbox_result


class CellNumberRenderer:
    def __init__(
        self, name: str, project_name: str, patient_id: int, cell_type: str
    ):
        self.name = name
        self.project_name = project_name
        self.patient_id = patient_id
        self.cell_type = cell_type
        self.data_list = (
            []
            if (self.cell_type is None) | (self.patient_id is None)
            else self.get_data_list()
        )

    def get_data_list(self):
        sql = f"""SELECT cell_number 
                FROM {self.project_name}_cell 
                WHERE cell_type = '{self.cell_type}' 
                AND patient_id = {self.patient_id} 
                ORDER BY cell_number"""

        return return_selectbox_result([data["cell_number"] for data in query_database(sql)])  # type: ignore

    def render(self):
        return st.selectbox(self.name, self.data_list, index=0)


class FilterCellNumberRenderer(CellNumberRenderer):
    def __init__(self, name, project_name, patient_id, cell_type, label_type):
        self.label_type = label_type
        super().__init__(name, project_name, patient_id, cell_type)


class FilterQualityCellNumberRenderer(FilterCellNumberRenderer):
    def get_data_list(self):
        sql = f"""SELECT distinct(cell_number) 
                FROM {self.project_name}_cell 
                WHERE cell_type = '{self.cell_type}' 
                AND patient_id = {self.patient_id} 
                AND cell_id IN 
                    (SELECT distinct(cell_id) FROM {self.project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_{self.label_type})) 
                ORDER BY cell_number"""

        logging.info(sql)
        logging.info([data["cell_number"] for data in query_database(sql)])

        return return_selectbox_result(
            [data["cell_number"] for data in query_database(sql)]
        )


class FilterCenterCellNumberRenderer(FilterCellNumberRenderer):
    def get_data_list(self):
        sql = f"""SELECT distinct(cell_number) 
                FROM {self.project_name}_cell 
                WHERE cell_type = '{self.cell_type}' 
                AND patient_id = {self.patient_id} 
                AND cell_id IN 
                    (SELECT distinct(cell_id) 
                    FROM {self.project_name}_image 
                    WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_{self.label_type})
                    AND image_type = 'HOLOTOMOGRAPHY') 
                ORDER BY cell_number"""
        logging.info(sql)
        logging.info([data["cell_number"] for data in query_database(sql)])
        return return_selectbox_result(
            [data["cell_number"] for data in query_database(sql)]
        )


class CellNumberRendererFactory:
    factory_dict = {
        "quality": FilterQualityCellNumberRenderer,
        "center": FilterCenterCellNumberRenderer,
    }

    def get_renderer(
        self,
        name: str,
        project_name: str,
        patient_id: int,
        cell_type: str,
        filtered: bool,
        label_type: str,
    ):
        return (
            self.factory_dict[label_type](
                name, project_name, patient_id, cell_type, label_type
            )
            if filtered
            else CellNumberRenderer(name, project_name, patient_id, cell_type)
        )
