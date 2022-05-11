import streamlit as st

from src.database import query_database
from src.renderer import OptionRenderer


def get_project_list():
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


def return_result(lst):
    return lst if lst is not None else []


class ProjectListRenderer:
    def __init__(self, name: str):
        self.name = name
        self.data_list = self.get_datalist()

    def get_datalist(self):
        data_list = get_project_list()
        return [] if data_list is None else data_list

    def render(self):
        return st.selectbox(self.name, self.data_list)


class PatientListRenderer:
    def __init__(self, name: str, project_name: str):
        self.name = name
        self.project_name = project_name
        self.data_list = self.get_datalist()

    def get_datalist(self):
        data_list = query_database(
            f"SELECT patient_id FROM {self.project_name}_patient"
        )

        return return_result([data["patient_id"] for data in data_list])  # type: ignore

    def render(self):
        return st.selectbox(self.name, self.data_list, index=0)


class FilterQualityPatientListRenderer(PatientListRenderer):
    def __init__(self, name, project_name, label_type):
        self.label_type = label_type
        super().__init__(name, project_name)

    def get_datalist(self):
        data_list = query_database(
            f"""SELECT distinct(patient_id) 
                FROM {self.project_name}_cell 
                WHERE cell_id IN 
                    (SELECT distinct(cell_id) 
                    FROM {self.project_name}_image 
                    WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_{self.label_type}))
            """
        )
        return return_result([data["patient_id"] for data in data_list])


class FilterCenterPatientListRenderer(PatientListRenderer):
    def __init__(self, name, project_name, label_type):
        self.label_type = label_type
        super().__init__(name, project_name)

    def get_datalist(self):
        data_list = query_database(
            f"""SELECT distinct(patient_id) 
                FROM {self.project_name}_cell 
                WHERE cell_id IN 
                    (SELECT distinct(cell_id) 
                    FROM {self.project_name}_image 
                    WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_{self.label_type}) AND image_type = 'HOLOTOMOGRAPHY')
            """
        )
        return return_result([data["patient_id"] for data in data_list])


class PatientListRendererFactory:
    factory_dict = {
        "quality": FilterQualityPatientListRenderer,
        "center": FilterCenterPatientListRenderer,
    }

    def get_renderer(
        self, name: str, project_name: str, filtered: bool, label_type: str
    ):
        return (
            self.factory_dict[label_type](name, project_name, label_type)
            if filtered
            else PatientListRenderer(name, project_name)
        )


class CellTypeRenderer:
    def __init__(self, project_name, patient_id, label_type):
        self.project_name = project_name
        self.patient_id = patient_id
        self.label_type = label_type
        self.data_list = (
            None if self.patient_id is None else self.get_data_list()
        )

    def get_data_list(self):
        sql = f"""SELECT distinct(cell_type) 
                FROM {self.project_name}_cell 
                WHERE patient_id = {self.patient_id} 
                ORDER BY cell_type"""

        return [data["cell_type"] for data in query_database(sql)]  # type: ignore

    def render(self):
        if self.data_list is not None:
            return st.selectbox("Cell type", self.data_list, index=0)
        else:
            return st.selectbox("Cell type", [])


class FilterCellTypeRenderer(CellTypeRenderer):
    def get_celltype_list(self):
        sql = f"""SELECT distinct(cell_type) 
                FROM {self.project_name}_cell 
                WHERE patient_id = {self.patient_id} 
                AND cell_id IN 
                    (SELECT distinct(cell_id) 
                    FROM {self.project_name}_image 
                    WHERE image_id NOT IN (SELECT image_id FROM {self.project_name}_image_{self.label_type}))
                ORDER BY cell_type"""

        return [data["cell_type"] for data in query_database(sql)]  # type: ignore


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
            FilterCellTypeRenderer(
                project_name, patient_id, label_type
            ).render()
            if filter_labeled
            else CellTypeRenderer(project_name, patient_id, label_type).render()
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
