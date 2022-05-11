import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import streamlit as st
import tifffile
from PIL import Image
from streamlit_custom_image_labeller import st_custom_image_labeller

from src.cell_selector import render_cell_selector
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


@dataclass
class Point:
    x: int
    y: int
    z: int


def set_default_point(
    project_name: str, image_id: int, image_size: tuple[int, int, int]
):

    data = query_database(
        f"SELECT image_id, x, y, z FROM {project_name}_image_center WHERE image_id = {image_id}"
    )

    default_point = Point(
        image_size[1] // 2, image_size[2] // 2, image_size[0] // 2
    )

    x = data[0].get("x", default_point.x) if data is not () else default_point.x
    y = data[0].get("x", default_point.y) if data is not () else default_point.y
    z = data[0].get("x", default_point.z) if data is not () else default_point.z

    st.session_state["point"] = Point(x, y, z)


def render_center_labeller(image: np.ndarray, point: Point):
    col1, col2 = st.columns(2)

    with col1:
        st.header("HT - XY")
        logging.info(f"render col1 - {st.session_state['point']}")
        output = st_custom_image_labeller(
            TomocubeImage.numpy_to_image(
                TomocubeImage.slice_axis(
                    image, idx=st.session_state["point"].z, axis=0
                )
            ),
            point_color="red",
            point=(
                st.session_state["point"].y,
                st.session_state["point"].x,
            ),  # numpy array axis is not matching with mouse point axis
        )
        st.session_state["point"].y = output[
            "x"
        ]  # numpy array axis is not matching with mouse point axis
        st.session_state["point"].x = output[
            "y"
        ]  # numpy array axis is not matching with mouse point axis

    with col2:
        st.header("HT - YZ")
        logging.info(f"render col2 - {st.session_state['point']}")
        output2 = st_custom_image_labeller(
            TomocubeImage.numpy_to_image(
                TomocubeImage.slice_axis(
                    image, idx=st.session_state["point"].y, axis=2
                )
            ),
            point_color="red",
            point=(st.session_state["point"].x, st.session_state["point"].z),
        )

        st.session_state["point"].z = output2["y"]


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
        value=getattr(st.session_state.point, factory[axis]),
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
    filter_labeled = True

    TitleRenderer("Tomocube Image Quality Labeller").render()

    (
        filter_labeled,
        project_name,
        patient_id,
        cell_type,
        cell_number,
    ) = render_cell_selector(filter_labeled, label_type="center")

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

    image = TomocubeImage(ht_path).process()

    if "point" not in st.session_state:
        set_default_point(project_name, ht_cellimage.image_id, image.shape)

    render_center_labeller(image, st.session_state.point)

    st.write(
        f"The coordinates of center point: ({st.session_state['point'].x}, {st.session_state['point'].y}, {st.session_state['point'].z})"
    )

    if st.button("Save Point"):
        write_to_database(
            project_name,
            ht_cellimage.image_id,
            st.session_state["point"].x,
            st.session_state["point"].y,
            st.session_state["point"].z,
        )

    if show_all_axis := st.checkbox("Show all axis", value=False):
        render_morphology_all_axis(image)
