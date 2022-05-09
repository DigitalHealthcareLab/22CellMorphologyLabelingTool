import streamlit as st

from src.renderer import (
    CellNumberRenderer,
    CellTypeRenderer,
    FilterCellNumberRenderer,
    FilterCellTypeRenderer,
    FilterPatientListRenderer,
    OptionRenderer,
    PatientListRenderer,
    ProjectListRenderer,
)


def render_sidebar(filter_labeled):
    with st.sidebar:
        st.write("Options:")
        option_renderer = OptionRenderer("Filter labeled", filter_labeled)
        filter_labeled = option_renderer.render()

        project_name = ProjectListRenderer().render()
        patient_id = (
            FilterPatientListRenderer(project_name).render()
            if filter_labeled
            else PatientListRenderer(project_name).render()
        )
        cell_type = (
            FilterCellTypeRenderer(project_name, patient_id).render()
            if filter_labeled
            else CellTypeRenderer(project_name, patient_id).render()
        )
        cell_number = (
            FilterCellNumberRenderer(
                project_name, patient_id, cell_type
            ).render()
            if filter_labeled
            else CellNumberRenderer(
                project_name, patient_id, cell_type
            ).render()
        )

    return filter_labeled, project_name, patient_id, cell_type, cell_number
