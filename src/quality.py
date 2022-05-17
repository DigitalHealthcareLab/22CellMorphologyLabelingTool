import streamlit as st

from src.database import Database, query_database


def get_default_quality(project_name, image_id: int, key: str):
    data = query_database(
        f"SELECT quality FROM {project_name}_image_quality WHERE image_id = {image_id}"
    )
    st.session_state[key] = None if data is () else data[0].get("quality")


def save_quality(project_name, image_ids: tuple[int], quality):
    database = Database()
    num_quality = 0 if quality == "Good" else 1
    for image_id in image_ids:
        sql = f"INSERT INTO {project_name}_image_quality (image_id, quality) VALUES ({image_id}, {num_quality}) ON DUPLICATE KEY UPDATE quality = {num_quality}"
        database.execute_sql(sql)
    database.conn.commit()
    database.conn.close()

