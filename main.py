import streamlit as st

from src.database import query_database
from src.gdrive import GDriveCredential, GDriveDownloader
from src.image import download_image, render_image
from src.sidebar import (
    get_cell_number,
    get_cell_type,
    get_patient_list,
    get_project_list,
)


def get_images(project_name, patient_id, cell_type, cell_number):
    sql = f"SELECT image_id, google_drive_file_id, create_date, image_type FROM {project_name}_image WHERE cell_id = (SELECT cell_id FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND cell_number = {cell_number} AND patient_id = {patient_id})"
    result = query_database(sql)
    bf = get_google_drive_id(result, "BRIGHT_FIELD")
    mip = get_google_drive_id(result, "MIP")
    ht = get_google_drive_id(result, "HOLOTOMOGRAPHY")
    return bf, mip, ht


def get_google_drive_id(data_list, image_type):
    return [
        data["google_drive_file_id"]
        for data in data_list
        if data["image_type"] == image_type
    ][0]


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

    credentials = GDriveCredential().credentials
    downloader = GDriveDownloader(credentials)
    bf_path = download_image(downloader, bf_image, "image", "bf.tiff")
    mip_path = download_image(downloader, mip_image, "image", "mip.tiff")

    col1, col2 = st.columns(2)
    with col1:
        render_image(bf_path)

    with col2:
        render_image(mip_path)


if __name__ == "__main__":
    main()
