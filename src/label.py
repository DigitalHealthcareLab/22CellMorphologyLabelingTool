from typing import Union

import streamlit as st

from src.database import Database, query_database


def get_default_quality(project_name, image_id) -> Union[int, None]:
    result = query_database(
        f"SELECT quality FROM {project_name}_image_quality WHERE image_id = {image_id}"
    )
    if len(result) == 0:
        return None
    elif result[0]["quality"] == 0:
        return "Good"
    elif result[0]["quality"] == 1:
        return "Bad"


def save_quality(project_name, image_id, quality):
    database = Database()
    num_quality = 0 if quality == "Good" else 1
    sql = f"INSERT INTO {project_name}_image_quality (image_id, quality) VALUES ({image_id}, {num_quality}) ON DUPLICATE KEY UPDATE quality = {num_quality}"
    database.execute_sql(sql)
    database.conn.commit()
    database.conn.close()
    del database
