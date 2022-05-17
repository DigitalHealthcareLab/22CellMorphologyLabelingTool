import logging

import streamlit as st

from src.cell_number_selector import CellNumberRendererFactory
from src.cell_type_selector import CellTypeRendererFactory
from src.patient_id_selector import PatientListRendererFactory
from src.project_selector import ProjectListRenderer
from src.renderer import OptionRenderer


def render_cell_selector(label_type):
    logging.info("Render Sidebar Cell Selector")
    with st.sidebar:
        st.write("Options:")
        option_renderer = OptionRenderer(
            "Filter labeled", st.session_state[f"{label_type}_filter_labeled"]
        )
        st.session_state[
            f"{label_type}_filter_labeled"
        ] = option_renderer.render()

        st.session_state[f"{label_type}_project_name"] = ProjectListRenderer(
            "Tomocube project"
        ).render()

        st.session_state[f"{label_type}_patient_id"] = (
            PatientListRendererFactory()
            .get_renderer(
                "Patient ID",
                st.session_state[f"{label_type}_project_name"],
                st.session_state[f"{label_type}_filter_labeled"],
                label_type,
            )
            .render()
        )
        st.session_state[f"{label_type}_cell_type"] = (
            CellTypeRendererFactory()
            .get_renderer(
                "Cell Type",
                st.session_state[f"{label_type}_project_name"],
                st.session_state[f"{label_type}_patient_id"],
                st.session_state[f"{label_type}_filter_labeled"],
                label_type,
            )
            .render()
        )
        st.session_state[f"{label_type}_cell_number"] = (
            CellNumberRendererFactory()
            .get_renderer(
                "Cell Number",
                st.session_state[f"{label_type}_project_name"],
                st.session_state[f"{label_type}_patient_id"],
                st.session_state[f"{label_type}_cell_type"],
                st.session_state[f"{label_type}_filter_labeled"],
                label_type,
            )
            .render()
        )
