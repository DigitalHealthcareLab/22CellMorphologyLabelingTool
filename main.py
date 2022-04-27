import streamlit as st

from src.database import query_database
from src.gdrive import GDriveCredential, GDriveDownloader
from src.image import download_image, get_images, render_image
from src.label import get_default_quality, save_quality
from src.sidebar import (
    get_cell_number,
    get_cell_type,
    get_patient_list,
    get_project_list,
)


def render_title():
    st.title("""Tomocube Image Quality Labeller""")


def render_sidebar(filter_labeled):
    with st.sidebar:
        filter_labeled = st.checkbox("Filter out labeled", value=filter_labeled)

        project_list = get_project_list()
        project_name = st.selectbox("Tomocube project", project_list)

        patient_list = get_patient_list(project_name)
        patient_id = st.selectbox("Patient ID", patient_list, index=0)

        cell_type_list = get_cell_type(project_name, patient_id, filter_labeled)
        cell_type = st.selectbox("Cell type", cell_type_list, index=0)

        cell_number_list = get_cell_number(
            project_name, patient_id, cell_type, filter_labeled
        )
        cell_number = st.selectbox("Cell number", cell_number_list, index=0)

        def get_total_cell_count(project_name) -> int:
            return query_database(f"SELECT COUNT(*) FROM {project_name}_cell")[
                0
            ].get("COUNT(*)")

        def get_labelled_cell_count(project_name) -> int:
            return query_database(
                f"SELECT count(distinct(i.cell_id)) as cell_count FROM {project_name}_image_quality q LEFT JOIN {project_name}_image i ON q.image_id = i.image_id"
            )[0].get("cell_count")

        total_cell_count = get_total_cell_count(project_name)
        total_labelled_cell_count = get_labelled_cell_count(project_name)

        st.write("The number of labeled cell:", total_labelled_cell_count)
        st.write(
            "The number of unlabeled cell:",
            total_cell_count - total_labelled_cell_count,
        )
        st.write(
            f"Progress: {total_labelled_cell_count / total_cell_count * 100:.0f}%"
        )
        my_bar = st.progress(total_labelled_cell_count / total_cell_count)
    return filter_labeled, project_name, patient_id, cell_type, cell_number


def render_images(
    project_name, bf_cellimage, mip_cellimage, ht_cellimage, bf_path, mip_path
):
    col1, col2 = st.columns(2)
    with col1:
        render_image(bf_path)
        bf_quality = render_image_quality(
            project_name, (bf_cellimage.image_id,)
        )

    with col2:
        render_image(mip_path)
        mip_default_quality = render_image_quality(
            project_name, (mip_cellimage.image_id, ht_cellimage.image_id)
        )


def render_image_quality(project_name, cellimages):
    quality = get_default_quality(project_name, cellimages)
    if quality == "Good":
        st.success("Good")
    elif quality == "Bad":
        st.error("Bad")
    elif quality is None:
        st.warning("No quality label")
    return quality


def render_label_buttons(
    project_name, bf_cellimage, mip_cellimage, ht_cellimage
):
    col1, col2, col3, col4 = st.columns(4)
    col1.button(
        "Good",
        on_click=save_quality,
        args=(project_name, (bf_cellimage.image_id,), "Good"),
        key="bf_good",
    )
    col2.button(
        "Bad",
        on_click=save_quality,
        args=(project_name, (bf_cellimage.image_id,), "Bad"),
        key="bf_bad",
    )
    col3.button(
        "Good",
        on_click=save_quality,
        args=(
            project_name,
            (mip_cellimage.image_id, ht_cellimage.image_id),
            "Good",
        ),
        key="mip_good",
    )
    col4.button(
        "Bad",
        on_click=save_quality,
        args=(
            project_name,
            (mip_cellimage.image_id, ht_cellimage.image_id),
            "Bad",
        ),
        key="mip_bad",
    )


def main():
    filter_labeled = True
    credentials = GDriveCredential().credentials
    downloader = GDriveDownloader(credentials)

    render_title()

    (
        filter_labeled,
        project_name,
        patient_id,
        cell_type,
        cell_number,
    ) = render_sidebar(filter_labeled)

    bf_cellimage, mip_cellimage, ht_cellimage = get_images(
        project_name, patient_id, cell_type, cell_number
    )

    bf_path = download_image(
        downloader, bf_cellimage.image_google_id, "image", "bf.tiff"
    )
    mip_path = download_image(
        downloader, mip_cellimage.image_google_id, "image", "mip.tiff"
    )

    render_images(
        project_name,
        bf_cellimage,
        mip_cellimage,
        ht_cellimage,
        bf_path,
        mip_path,
    )

    render_label_buttons(
        project_name, bf_cellimage, mip_cellimage, ht_cellimage
    )


if __name__ == "__main__":
    main()
