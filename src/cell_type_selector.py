import streamlit as st

from src.database import query_database
from src.renderer import return_selectbox_result


class CellTypeRenderer:
    def __init__(self, name: str, project_name: str, patient_id: int):
        self.name = name
        self.project_name = project_name
        self.patient_id = patient_id
        self.data_list = self.get_data_list() if patient_id is not None else []

    def get_data_list(self):
        sql = f"""SELECT distinct(cell_type) 
                FROM {self.project_name}_cell 
                WHERE patient_id = {self.patient_id} 
                ORDER BY cell_type"""
        return return_selectbox_result(
            [data["cell_type"] for data in query_database(sql)]
        )

    def render(self):
        return st.selectbox(self.name, self.data_list, index=0)


class FilterCellTypeRenderer(CellTypeRenderer):
    def __init__(
        self, name: str, project_name: str, patient_id: int, label_type: str
    ):
        self.label_type = label_type
        super().__init__(name, project_name, patient_id)


class FilterQualityCellTypeRenderer(FilterCellTypeRenderer):
    def get_celltype_list(self):
        sql = f"""SELECT distinct(cell_type) 
                FROM {self.project_name}_cell 
                WHERE patient_id = {self.patient_id} 
                AND cell_id IN 
                    (SELECT distinct(cell_id) 
                    FROM {self.project_name}_image 
                    WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_{self.label_type}))
                ORDER BY cell_type"""

        return return_selectbox_result([data["cell_type"] for data in query_database(sql)])  # type: ignore


class FilterCenterCellTypeRenderer(FilterCellTypeRenderer):
    def get_celltype_list(self):
        sql = f"""SELECT distinct(cell_type) 
                FROM {self.project_name}_cell 
                WHERE patient_id = {self.patient_id} 
                AND cell_id IN 
                    (SELECT distinct(cell_id) 
                    FROM {self.project_name}_image 
                    WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_{self.label_type})
                    AND image_type = 'HOLOTOMOGRAPHY' )
                ORDER BY cell_type"""

        return return_selectbox_result([data["cell_type"] for data in query_database(sql)])  # type: ignore


class CellTypeRendererFactory:
    factory_dict = {
        "quality": FilterQualityCellTypeRenderer,
        "center": FilterCenterCellTypeRenderer,
    }

    def get_renderer(
        self,
        name: str,
        project_name: str,
        patient_id: int,
        filtered: bool,
        label_type: str,
    ):
        return (
            self.factory_dict[label_type](
                name, project_name, patient_id, label_type
            )
            if filtered
            else CellTypeRenderer(name, project_name, patient_id)
        )
