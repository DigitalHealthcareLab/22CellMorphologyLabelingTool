import streamlit as st

from src.database import Database


def query_database(sql):
    database = Database()
    data_list = database.execute_sql(sql)
    database.conn.close()
    del database
    return data_list


def get_project_list():
    data_list = query_database("SELECT project_id, name FROM project")
    return [data["name"] for data in data_list]


def get_patient_list(project_name: str):
    data_list = query_database(f"SELECT patient_id FROM {project_name}_patient")
    return [data["patient_id"] for data in data_list]


def get_cell_type(project_name: str):
    data_list = query_database(
        f"SELECT distinct(cell_type) FROM {project_name}_cell ORDER BY cell_type"
    )
    return [data["cell_type"] for data in data_list]


def get_cell_number(project_name: str, patient_id: int, cell_type: str):
    data_list = query_database(
        f"SELECT cell_number FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND patient_id = {patient_id} ORDER BY cell_number"
    )
    return [data["cell_number"] for data in data_list]


def get_images(project_name, patient_id, cell_type, cell_number):
    sql = f"SELECT image_id, google_drive_file_id, create_date, image_type FROM {project_name}_image WHERE cell_id = (SELECT cell_id FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND cell_number = {cell_number} AND patient_id = {patient_id})"
    database = Database()
    result = database.execute_sql(sql)
    database.conn.close()
    del database
    bf = [
        data["google_drive_file_id"]
        for data in result
        if data["image_type"] == "BRIGHT_FIELD"
    ][0]
    mip = [
        data["google_drive_file_id"]
        for data in result
        if data["image_type"] == "MIP"
    ][0]
    ht = [
        data["google_drive_file_id"]
        for data in result
        if data["image_type"] == "HOLOTOMOGRAPHY"
    ][0]
    return bf, mip, ht


def main():
    st.title("""Tomocube Image Quality Labeller""")
    st.write("""Author: MinDong Sung""")

    with st.sidebar:
        project_name = st.selectbox("Tomocube project", (get_project_list()))
        patient_id = st.selectbox(
            "Patient ID", (get_patient_list(project_name))
        )
        cell_type = st.selectbox("Cell type", (get_cell_type(project_name)))
        cell_number = st.selectbox(
            "Cell number",
            (get_cell_number(project_name, patient_id, cell_type)),
        )
    bf_image, mip_image, ht_image = get_images(
        project_name, patient_id, cell_type, cell_number
    )
    st.write(f"BF:{bf_image}")
    st.write(f"MIP:{mip_image}")
    st.write(f"HT:{ht_image}")


if __name__ == "__main__":
    main()
