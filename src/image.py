from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image


def download_image(
    downloader, google_file_id, download_path, download_filename
):
    downloader.download(google_file_id, download_path, download_filename)
    return Path(download_path, download_filename)


def normalize_image(image_arr: np.ndarray) -> Image:
    return Image.fromarray(
        np.round(
            (image_arr - image_arr.min())
            / (image_arr.max() - image_arr.min())
            * 255
        ).astype(np.uint8)
    )  # type: ignore


def render_image(image_file):
    image = Image.open(image_file)
    image_arr = np.array(image)

    if image_arr.min() > 255:
        image = normalize_image(image_arr)

    st.image(image, width=350)


if __name__ == "__main__":
    bf_image = Image.open("image/bf.tiff")
    mip_image = Image.open("image/mip.tiff")
