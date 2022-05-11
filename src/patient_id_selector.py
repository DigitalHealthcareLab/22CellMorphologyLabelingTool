import streamlit as st

from src.database import query_database
from src.renderer import return_selectbox_result


class PatientListRenderer:
    def __init__(self, name: str, project_name: str):
        self.name = name
        self.project_name = project_name
        self.data_list = self.get_datalist()

    def get_datalist(self):
        data_list = query_database(
            f"SELECT patient_id FROM {self.project_name}_patient"
        )

        return return_selectbox_result([data["patient_id"] for data in data_list])  # type: ignore

    def render(self):
        return st.selectbox(self.name, self.data_list, index=0)


class FilterPatientListRenderer(PatientListRenderer):
    def __init__(self, name, project_name, label_type):
        self.label_type = label_type
        super().__init__(name, project_name)


class FilterQualityPatientListRenderer(FilterPatientListRenderer):
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
        return return_selectbox_result(
            [data["patient_id"] for data in data_list]
        )


class FilterCenterPatientListRenderer(FilterPatientListRenderer):
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
        return return_selectbox_result(
            [data["patient_id"] for data in data_list]
        )


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
