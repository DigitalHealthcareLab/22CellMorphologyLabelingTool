from pathlib import Path

import numpy as np
import streamlit as st
import tifffile
from PIL import Image
from streamlit_custom_image_labeller import st_custom_image_labeller

from src.cell_sidebar import render_sidebar
from src.database import Database, query_database
from src.gdrive import GDriveCredential, GDriveDownloader
from src.image import download_image, get_images
from src.renderer import TitleRenderer


class TomocubeImage:
    def __init__(self, image_path: Path):
        self.image_path = image_path

    def process(self):
        image_arr = self.read_image()
        image_arr = self.normalize_img(image_arr)
        return image_arr

    def read_image(self) -> np.ndarray:
        return tifffile.imread(str(self.image_path))

    @staticmethod
    def normalize_img(img: np.ndarray) -> np.ndarray:
        return (img - np.min(img)) / (np.max(img) - np.min(img)) * 255

    @staticmethod
    def numpy_to_image(img_arr: np.ndarray) -> Image.Image:
        return Image.fromarray(img_arr)

    @staticmethod
    def slice_axis(img_arr: np.ndarray, idx: int, axis: int) -> np.ndarray:
        return img_arr.take(indices=idx, axis=axis)

    @classmethod
    def image_for_streamlit(
        cls, img_arr: np.ndarray, idx: int, axis: int
    ) -> Image.Image:
        return cls.numpy_to_image(
            cls.slice_axis(img_arr, idx, axis).astype(np.uint8)
        )


def set_default_state(project_name:str, image_id:int, image_size:tuple[int, int, int]):
    data = query_database(
        f"SELECT image_id, x, y, z FROM {project_name}_image_center WHERE image_id = {image_id}"
    )
    if len(data) >= 1:
        st.session_state["x"] = data[0].get("x", image_size[1] // 2)
        st.session_state["y"] = data[0].get("y", image_size[2] // 2)
        st.session_state["z"] = data[0].get("z", image_size[0] // 2)
    elif len(data) == 0:
        st.session_state["x"] = image_size[1] // 2
        st.session_state["y"] = image_size[2] // 2
        st.session_state["z"] = image_size[0] // 2

def render_center_labeller(image: np.ndarray):
    col1, col2 = st.columns(2)

    with col1:
        st.header("HT - XY")
        output = st_custom_image_labeller(
            TomocubeImage.numpy_to_image(
                TomocubeImage.slice_axis(
                    image, idx=st.session_state["z"], axis=0
                )
            ),
            point=(
                st.session_state["y"],
                st.session_state["x"],
            ),  # numpy array axis is not matching with mouse point axis
        )
        st.session_state["y"] = output[
            "x"
        ]  # numpy array axis is not matching with mouse point axis
        st.session_state["x"] = output[
            "y"
        ]  # numpy array axis is not matching with mouse point axis

    with col2:
        st.header("HT - YZ")
        output2 = st_custom_image_labeller(
            TomocubeImage.numpy_to_image(
                TomocubeImage.slice_axis(
                    image, idx=st.session_state["y"], axis=2
                )
            ),
            point=(st.session_state["x"], st.session_state["z"]),
        )
        st.session_state["z"] = output2["y"]


def render_morphology_all_axis(image: np.ndarray) -> None:
    st.subheader("Morphology")

    col1, col2, col3 = st.columns(3)
    with col1:
        _render_each_axis(image, 0)
    with col2:
        _render_each_axis(image, 1)
    with col3:
        _render_each_axis(image, 2)


def _render_each_axis(image: np.ndarray, axis: int) -> None:
    factory = {0: "z", 1: "x", 2: "y"}
    slider_value = st.slider(
        f"{factory[axis]}-axis",
        0,
        image.shape[axis] - 1,
        value=getattr(st.session_state, factory[axis]),
    )

    st.image(
        TomocubeImage.image_for_streamlit(image, idx=slider_value, axis=axis),
        use_column_width=True,
        clamp=True,
    )


def write_to_database(project_name, image_id, x, y, z):
    database = Database()
    sql = f"INSERT INTO {project_name}_image_center (image_id, x, y, z) VALUES ({image_id}, {x}, {y}, {z}) ON DUPLICATE KEY UPDATE x = {x}, y = {y}, z = {z}"
    database.execute_sql(sql)
    database.conn.commit()
    database.conn.close()
    del database


def app():
    downloader = GDriveDownloader(GDriveCredential().credentials)

    filter_labeled = False

    TitleRenderer("Tomocube Image Quality Labeller").render()

    (
        filter_labeled,
        project_name,
        patient_id,
        cell_type,
        cell_number,
    ) = render_sidebar(filter_labeled)

    if (cell_type == "Not Available") | (cell_number == "Not Available"):
        st.write("Not Available images")
        st.write(
            "Please uncheck filter out labeled or check the images really exist."
        )
    else:
        _, _, ht_cellimage = get_images(
            project_name, patient_id, cell_type, cell_number
        )

    if ht_cellimage is not None:
        ht_path = download_image(
            downloader, ht_cellimage.image_google_id, "image", "ht.tiff"
        )
    else:
        ht_path = None

    if ht_path is None:
        return

    sample_3d_image = TomocubeImage(ht_path).process()

    image_size = sample_3d_image.shape
    set_default_state(project_name, ht_cellimage.image_id, image_size)

    render_center_labeller(sample_3d_image)

    write_to_database(
        project_name,
        ht_cellimage.image_id,
        st.session_state["x"],
        st.session_state["y"],
        st.session_state["z"],
    )

    st.write(
        st.session_state["x"], st.session_state["y"], st.session_state["z"]
    )

    if show_all_axis := st.checkbox("Show all axis", value=False):
        render_morphology_all_axis(sample_3d_image)


### sql for create table
# CREATE TABLE 2022_tomocube_lungT_image_center(
#    image_id INT(10) NOT NULL,
# 	x INT(5) NOT NULL,
# 	y INT(5) NOT NULL,
#    z INT(5) NOT NULL,
#    PRIMARY KEY (`image_id`)
# )
