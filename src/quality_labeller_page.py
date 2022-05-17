import streamlit as st

from src.cell_selector import render_cell_selector
from src.gdrive import GDriveCredential, GDriveDownloader
from src.image import TomocubeImage, download_image, get_images
from src.quality import get_default_quality, save_quality
from src.renderer import LabelProgressRenderer, TitleRenderer
from src.session import set_session_state


def render_image_quality(quality: int) -> None:
    if quality == 0:
        st.success("Good")
    elif quality == 1:
        st.error("Bad")
    elif quality is None:
        st.warning("No quality label")


def app():
    set_session_state(
        "quality_filter_labeled",
        "quality_project_name",
        "quality_patient_id",
        "quality_cell_type",
        "quality_cell_number",
    )
    st.session_state["quality_filter_labeled"] = True

    set_session_state(
        "bf_image_meta",
        "mip_image_meta",
        "ht_image_meta_quality",
        "bf_image",
        "mip_image",
        "bf_quality",
        "mip_quality",
    )

    downloader = GDriveDownloader(GDriveCredential().credentials)
    TitleRenderer("Tomocube Image Quality Labeller").render()

    render_cell_selector(label_type="quality")

    if (st.session_state["quality_cell_type"] == "Not Available") | (
        st.session_state["quality_cell_number"] == "Not Available"
    ):
        st.write("Not Available images")
        st.write(
            "Please uncheck filter out labeled or check the images really exist."
        )
        return

    bf_cellimage, mip_cellimage, ht_cellimage = get_images(
        st.session_state["quality_project_name"],
        st.session_state["quality_patient_id"],
        st.session_state["quality_cell_type"],
        st.session_state["quality_cell_number"],
    )

    if bf_cellimage != st.session_state["bf_image_meta"]:
        if bf_cellimage is not None:
            download_image(
                downloader,
                bf_cellimage.image_google_id,
                "image",
                "bf.tiff",
                "bf_image",
            )
            st.session_state["bf_image_meta"] = bf_cellimage
            get_default_quality(
                st.session_state["quality_project_name"],
                bf_cellimage.image_id,
                "bf_quality",
            )
        else:
            st.session_state["bf_image"] = None

    if mip_cellimage != st.session_state["mip_image_meta"]:
        if mip_cellimage is not None:
            download_image(
                downloader,
                mip_cellimage.image_google_id,
                "image",
                "mip.tiff",
                "mip_image",
            )
            st.session_state["mip_image_meta"] = mip_cellimage
            st.session_state["ht_image_meta_quality"] = ht_cellimage
            get_default_quality(
                st.session_state["quality_project_name"],
                mip_cellimage.image_id,
                "mip_quality",
            )
        else:
            st.session_state["mip_image"] = None

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state["bf_image"] is None:
            st.write("There is no BF image")
        else:
            TomocubeImage.render(st.session_state["bf_image"], 350)
            render_image_quality(st.session_state["bf_quality"])

    with col2:
        if mip_cellimage is None:
            st.write("There is no MIP image")
        else:
            TomocubeImage.render(st.session_state["mip_image"], 350)
            render_image_quality(st.session_state["mip_quality"])

    col1, col2, col3, col4 = st.columns(4)
    if st.session_state["bf_image"] is not None:
        col1.button(
            "Good",
            on_click=save_quality,
            args=(
                st.session_state["quality_project_name"],
                (st.session_state["bf_image_meta"].image_id,),
                "Good",
            ),
            key="bf_good",
        )
        col2.button(
            "Bad",
            on_click=save_quality,
            args=(
                st.session_state["quality_project_name"],
                (st.session_state["bf_image_meta"].image_id,),
                "Bad",
            ),
            key="bf_bad",
        )

    if st.session_state["mip_image"] is not None:
        col3.button(
            "Good",
            on_click=save_quality,
            args=(
                st.session_state["quality_project_name"],
                (
                    st.session_state["mip_image_meta"].image_id,
                    st.session_state["ht_image_meta_quality"].image_id,
                ),
                "Good",
            ),
            key="mip_good",
        )
        col4.button(
            "Bad",
            on_click=save_quality,
            args=(
                st.session_state["quality_project_name"],
                (
                    st.session_state["mip_image_meta"].image_id,
                    st.session_state["ht_image_meta_quality"].image_id,
                ),
                "Bad",
            ),
            key="mip_bad",
        )

    with st.sidebar:
        LabelProgressRenderer(
            st.session_state["quality_project_name"], "quality"
        ).render()
