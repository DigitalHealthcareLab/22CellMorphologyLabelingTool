from dataclasses import dataclass
from pathlib import Path
from typing import Union

import numpy as np
import streamlit as st
from PIL import Image

from src.database import query_database


@dataclass
class CellImage:
    image_id: int
    image_google_id: str


def get_images(
    project_name, patient_id, cell_type, cell_number
) -> tuple[
    Union[CellImage, None], Union[CellImage, None], Union[CellImage, None]
]:
    sql = f"""SELECT image_id, google_drive_file_id, create_date, image_type 
            FROM {project_name}_image 
            WHERE cell_id = (SELECT cell_id 
                            FROM {project_name}_cell 
                            WHERE cell_type = '{cell_type}' 
                            AND cell_number = {cell_number} 
                            AND patient_id = {patient_id})"""

    result = query_database(sql)
    bf = get_cellimage(result, "BRIGHT_FIELD")
    mip = get_cellimage(result, "MIP")
    ht = get_cellimage(result, "HOLOTOMOGRAPHY")
    return bf, mip, ht


def get_cellimage(data_list, image_type) -> Union[CellImage, None]:
    # sourcery skip: simplify-len-comparison, use-named-expression
    result = [data for data in data_list if data["image_type"] == image_type]
    if len(result) > 0:
        return CellImage(result[0]["image_id"], result[0]["google_drive_file_id"])  # type: ignore
    else:
        return None


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
