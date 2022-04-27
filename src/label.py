from typing import Union

import streamlit as st

from src.database import Database, query_database


def get_default_quality(
    project_name, image_ids: tuple[str]
) -> Union[str, None]:

    results = [
        query_database(
            f"SELECT quality FROM {project_name}_image_quality WHERE image_id = {image_id}"
        )
        for image_id in image_ids
    ]

    if len(results) == 1:
        if len(results[0]) == 0:
            return None
        elif results[0][0].get("quality", None) == 0:
            return "Good"
        elif results[0][0].get("quality", None) == 1:
            return "Bad"  # type: ignore

    elif len(results) == 2:
        if len(results[1]) == 0:
            return None

        if len(results[0]) == 0:
            return None

        elif (results[0][0].get("quality", None) == 0) and (
            results[1][0].get("quality", None) == 0
        ):
            return "Good"
        elif (results[0][0].get("quality", None) == 1) and (
            results[1][0].get("quality", None) == 1
        ):
            return "Bad"
        elif results[0][0].get("quality", None) != results[1][0].get(
            "quality", None
        ):
            return None


def save_quality(project_name, image_ids: tuple[str], quality):
    database = Database()
    num_quality = 0 if quality == "Good" else 1
    for image_id in image_ids:
        sql = f"INSERT INTO {project_name}_image_quality (image_id, quality) VALUES ({image_id}, {num_quality}) ON DUPLICATE KEY UPDATE quality = {num_quality}"
        database.execute_sql(sql)
    database.conn.commit()
    database.conn.close()
    del database
