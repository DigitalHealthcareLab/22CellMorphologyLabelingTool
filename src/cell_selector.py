import streamlit as st

from src.cell_number_selector import CellNumberRendererFactory
from src.cell_type_selector import CellTypeRendererFactory
from src.database import query_database
from src.patient_id_selector import PatientListRendererFactory
from src.project_selector import ProjectListRenderer
from src.renderer import OptionRenderer, return_selectbox_result


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
            CellNumberRendererFactory()
            .get_renderer(
                "Cell Number",
                project_name,
                patient_id,
                cell_type,
                filter_labeled,
                label_type,
            )
            .render()
        )

    return filter_labeled, project_name, patient_id, cell_type, cell_number
