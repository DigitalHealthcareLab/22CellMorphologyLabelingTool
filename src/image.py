from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Union

import numpy as np
import streamlit as st
from PIL import Image

from src.database import query_database


class ImageType(Enum):
    BRIGHT_FIELD = auto()
    MIP = auto()
    HOLOTOMOGRAPHY = auto()


@dataclass
class CellImageMeta:
    image_id: int
    image_google_id: str | None
    image_type: ImageType | None
    cell_type: str | None
    cell_number: int | None
    cell_id: int | None
    patient_id: int
    quality: Optional[int]

    @classmethod
    def from_image_id(cls, project_name, image_id) -> CellImageMeta:
        data = query_database(
            f"""SELECT 
                    i.image_id,
                    i.google_drive_file_id, 
                    i.image_type, 
                    c.cell_type, 
                    c.cell_number, 
                    i.cell_id, 
                    i.patient_id,
                    q.quality
                FROM (
                    SELECT * 
                    from {project_name}_image 
                    WHERE image_id = 1) i
                LEFT JOIN {project_name}_cell c
                ON c.cell_id = i.cell_id
                lEFT JOIN {project_name}_image_quality q
                ON i.image_id = q.image_id"""
        )
        return CellImageMeta(
            image_id,
            data[0].get("google_drive_file_id"),
            data[0].get("image_type"),
            data[0].get("cell_type"),
            data[0].get("cell_number"),
            data[0].get("cell_id"),
            data[0].get("patient_id"),
            data[0].get("quality", None),
        )

    @classmethod
    def from_cell_metadata(
        cls, project_name, patient_id, cell_type, cell_number
    ) -> list[CellImageMeta]:
        if (cell_type is None) | (cell_number is None):
            return []

        data = query_database(
            f"""SELECT i.image_id, i.google_drive_file_id, i.image_type, c.cell_type, c.cell_number, c.cell_id, c.patient_id, q.quality
                FROM (SELECT *
                    FROM {project_name}_cell 
                    WHERE cell_type = '{cell_type}'
                    AND cell_number = {cell_number}
                    AND patient_id = {patient_id}) c
                LEFT JOIN {project_name}_image i
                ON i.cell_id = c.cell_id
                LEFT JOIN {project_name}_image_quality q
                ON i.image_id = q.image_id"""
        )
        return [
            CellImageMeta(
                d.get("image_id"),
                d.get("google_drive_file_id"),
                d.get("image_type"),
                cell_type,
                cell_number,
                d.get("cell_id"),
                patient_id,
                d.get("quality", None),
            )  # type: ignore
            for d in data
        ]


def find_cell_image_by_image_type(
    cell_images: list[CellImageMeta], image_type: ImageType
) -> Union[CellImageMeta, None]:
    results = [
        cell_image
        for cell_image in cell_images
        if cell_image.image_type == image_type.name
    ]
    return results[0] if results else None


def get_images(
    project_name, patient_id, cell_type, cell_number
) -> tuple[
    Union[CellImageMeta, None],
    Union[CellImageMeta, None],
    Union[CellImageMeta, None],
]:
    cell_images = CellImageMeta.from_cell_metadata(
        project_name, patient_id, cell_type, cell_number
    )

    bf = find_cell_image_by_image_type(cell_images, ImageType.BRIGHT_FIELD)
    mip = find_cell_image_by_image_type(cell_images, ImageType.MIP)
    ht = find_cell_image_by_image_type(cell_images, ImageType.HOLOTOMOGRAPHY)

    return bf, mip, ht


def download_image(
    downloader, google_file_id, download_path, download_filename
):
    downloader.download(google_file_id, download_path, download_filename)
    return Path(download_path, download_filename)
