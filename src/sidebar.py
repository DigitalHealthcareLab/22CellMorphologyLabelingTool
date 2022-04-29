import streamlit as st

from src.database import query_database


def get_project_list():
    data_list = query_database("Show tables")
    return [
        data["Tables_in_tomocube"].replace("_patient", "")
        for data in data_list
        if "patient" in data["Tables_in_tomocube"]
    ]


def get_patient_list(project_name: str):
    data_list = query_database(f"SELECT patient_id FROM {project_name}_patient")
    return [data["patient_id"] for data in data_list]


def get_cell_type(
    project_name: str, patient_id: int, filter_labeled: bool = False
):  # sourcery skip: remove-redundant-if
    if filter_labeled:
        count_cell_type = query_database(
            f"SELECT count(distinct(cell_type)) as count_cell_type FROM {project_name}_cell WHERE patient_id = {patient_id} AND cell_id IN (SELECT distinct(cell_id) FROM {project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {project_name}_image_quality)) ORDER BY cell_type"
        )[0].get("count_cell_type", 0)

        if count_cell_type == 0:
            return None

        sql = f"SELECT count(distinct(cell_type)) as count_cell_type FROM {project_name}_cell WHERE patient_id = {patient_id} AND cell_id IN (SELECT distinct(cell_id) FROM {project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {project_name}_image_quality)) ORDER BY cell_type"

    elif not filter_labeled:
        sql = f"SELECT distinct(cell_type) FROM {project_name}_cell WHERE patient_id = {patient_id} ORDER BY cell_type"

    return [data["cell_type"] for data in query_database(sql)]  # type: ignore


def get_cell_number(
    project_name: str,
    patient_id: int,
    cell_type: str,
    filter_labeled: bool = False,
):  # sourcery skip: remove-redundant-if
    if filter_labeled:
        count_cell_number = query_database(
            f"SELECT count(distinct(cell_number)) as count_cell_number FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND patient_id = {patient_id} AND cell_id IN (SELECT distinct(cell_id) FROM {project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {project_name}_image_quality)) ORDER BY cell_number"
        )[0].get("count_cell_number")
        if count_cell_number > 0:
            sql = f"SELECT distinct(cell_number) FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND patient_id = {patient_id} AND cell_id IN (SELECT distinct(cell_id) FROM {project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {project_name}_image_quality)) ORDER BY cell_number"
        else:
            return None
    elif not filter_labeled:
        sql = f"SELECT cell_number FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND patient_id = {patient_id} ORDER BY cell_number"

    data_list = query_database(sql)
    return [data["cell_number"] for data in data_list]  # type: ignore


if __name__ == "__main__":
    print(get_project_list())
