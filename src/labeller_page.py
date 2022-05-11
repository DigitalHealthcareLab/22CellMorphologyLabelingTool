import streamlit as st

from src.cell_selector import render_cell_selector
from src.gdrive import GDriveCredential, GDriveDownloader
from src.image import download_image, get_images
from src.label import get_default_quality, save_quality
from src.renderer import CellImageRenderer, LabelProgressRenderer, TitleRenderer


def render_images(
    project_name, bf_cellimage, mip_cellimage, ht_cellimage, bf_path, mip_path
):
    col1, col2 = st.columns(2)
    with col1:
        if bf_cellimage is None:
            st.write("There is no BF image")
        else:
            CellImageRenderer(bf_path).render(350)
            bf_quality = render_image_quality(
                project_name, (bf_cellimage.image_id,)
            )

    with col2:
        if mip_cellimage is None:
            st.write("There is no MIP image")
        else:
            CellImageRenderer(mip_path).render(350)
            mip_quality = render_image_quality(
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
    if bf_cellimage is not None:
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

    if mip_cellimage is not None:
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


def app():
    filter_labeled = True
    downloader = GDriveDownloader(GDriveCredential().credentials)
    TitleRenderer("Tomocube Image Quality Labeller").render()

    (
        filter_labeled,
        project_name,
        patient_id,
        cell_type,
        cell_number,
    ) = render_cell_selector(filter_labeled, label_type="quality")

    with st.sidebar:
        LabelProgressRenderer(project_name).render()

    if (cell_type == "Not Available") | (cell_number == "Not Available"):
        st.write("Not Available images")
        st.write(
            "Please uncheck filter out labeled or check the images really exist."
        )
    else:
        bf_cellimage, mip_cellimage, ht_cellimage = get_images(
            project_name, patient_id, cell_type, cell_number
        )
        if bf_cellimage is not None:
            bf_path = download_image(
                downloader, bf_cellimage.image_google_id, "image", "bf.tiff"
            )
        else:
            bf_path = None

        if mip_cellimage is not None:
            mip_path = download_image(
                downloader, mip_cellimage.image_google_id, "image", "mip.tiff"
            )
        else:
            mip_path = None

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
