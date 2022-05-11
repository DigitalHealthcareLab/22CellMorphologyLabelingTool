import streamlit as st

from src.database import query_database
from src.renderer import return_selectbox_result


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


class ProjectListRenderer:
    def __init__(self, name: str):
        self.name = name
        self.data_list = self.get_datalist()

    def get_datalist(self):
        return return_selectbox_result(get_project_list())

    def render(self):
        return st.selectbox(self.name, self.data_list)
