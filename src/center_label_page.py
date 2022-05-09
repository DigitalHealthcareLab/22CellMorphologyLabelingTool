from dataclasses import dataclass
from pathlib import Path

import cv2 as cv
import numpy as np
import streamlit as st
import tifffile
from PIL import Image
from streamlit_custom_image_labeller import st_custom_image_labeller

from src.cell_sidebar import render_sidebar
from src.gdrive import GDriveCredential, GDriveDownloader
from src.image import download_image, get_images


@dataclass
class Point:
    x: int
    y: int
    z: int
    
    def write_to_database(project_name:str):
        pass


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


def read_multiple_tiff(filename):
    image = tifffile.imread(filename)
    norm = np.zeros((image.shape[1], image.shape[2]))
    final = cv.normalize(image, norm, 0, 255, cv.NORM_MINMAX)
    return final


def app():
    downloader = GDriveDownloader(GDriveCredential().credentials)

    filter_labeled = False

    st.title("Tomocube Cell Center Labeller")

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

    if "center" not in st.session_state:
        image_size = sample_3d_image.shape
        st.session_state["center"] = Point(
            image_size[1] // 2, image_size[2] // 2, image_size[0] // 2
        )
    col1, col2 = st.columns(2)

    with col1:
        st.header("HT - XY")
        output = st_custom_image_labeller(
            TomocubeImage.numpy_to_image(
                TomocubeImage.slice_axis(
                    sample_3d_image, idx=st.session_state["center"].z, axis=0
                )
            ),
            point=(
                st.session_state["center"].y,
                st.session_state["center"].x,
            ),  # numpy array axis is not matching with mouse point axis
        )
        st.session_state["center"].y = output[
            "x"
        ]  # numpy array axis is not matching with mouse point axis
        st.session_state["center"].x = output["y"]

    with col2:
        st.header("HT - YZ")
        output2 = st_custom_image_labeller(
            TomocubeImage.numpy_to_image(
                TomocubeImage.slice_axis(
                    sample_3d_image, idx=st.session_state["center"].y, axis=2
                )
            ),
            point=(st.session_state["center"].x, st.session_state["center"].z),
        )
        st.session_state["center"].z = output2["y"]

    st.write(st.session_state["center"])

    image = read_multiple_tiff(ht_path)

    ## streamlit code
    st.subheader("Morphology")
    col1, col2, col3 = st.columns(3)
    z = col1.slider(
        "z-axis", 0, image.shape[0] - 1, value=st.session_state["center"].z
    )
    col1.image(image[z, :, :], use_column_width=True, clamp=True)

    x = col2.slider(
        "x-axis", 0, image.shape[1] - 1, value=st.session_state["center"].x
    )
    col2.image(image[:, x, :], use_column_width=True, clamp=True)

    y = col3.slider(
        "y-axis", 0, image.shape[2] - 1, value=st.session_state["center"].y
    )
    col3.image(image[:, :, y], use_column_width=True, clamp=True)
