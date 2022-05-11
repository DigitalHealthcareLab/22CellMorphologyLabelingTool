import streamlit as st

from src.cell_type_selector import CellTypeRendererFactory
from src.database import query_database
from src.patient_id_selector import PatientListRendererFactory
from src.project_selector import ProjectListRenderer
from src.renderer import OptionRenderer, return_selectbox_result


def return_result(lst):
    return lst if lst is not None else []


class CellNumberRenderer:
    def __init__(self, project_name, patient_id, cell_type, label_type):
        self.project_name = project_name
        self.patient_id = patient_id
        self.cell_type = cell_type
        self.label_type = label_type
        self.cellnumber_list = (
            None
            if (self.cell_type is None) | (self.patient_id is None)
            else self.get_cellnumber_list()
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
                    (SELECT distinct(cell_id) FROM {self.project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_{self.label_type})) 
                ORDER BY cell_number"""

        return [data["cell_number"] for data in query_database(sql)]  # type: ignore


def render_cell_selector(filter_labeled, label_type):
    with st.sidebar:
        st.write("Options:")
        option_renderer = OptionRenderer("Filter labeled", filter_labeled)
        filter_labeled = option_renderer.render()

        project_name = ProjectListRenderer("Tomocube project").render()
        patient_id = (
            PatientListRendererFactory()
            .get_renderer(
                "Patient ID", project_name, filter_labeled, label_type
            )
            .render()
        )
        cell_type = (
            CellTypeRendererFactory()
            .get_renderer(
                "Cell Type",
                project_name,
                patient_id,
                filter_labeled,
                label_type,
            )
            .render()
        )
        cell_number = (
            FilterCellNumberRenderer(
                project_name, patient_id, cell_type, label_type
            ).render()
            if filter_labeled
            else CellNumberRenderer(
                project_name, patient_id, cell_type, label_type
            ).render()
        )

    return filter_labeled, project_name, patient_id, cell_type, cell_number
