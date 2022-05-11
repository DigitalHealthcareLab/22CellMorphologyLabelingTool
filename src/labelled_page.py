import numpy as np
import pandas as pd
import streamlit as st

from src.database import query_database
from src.project_selector import get_project_list
from src.renderer import TitleRenderer


def create_cell_metadata_table(project_name):
    sql = f"""
    SELECT t.project_id, t.patient_id, t.cell_type, t.image_type, quality, COUNT(t.image_type) num_image
    FROM 
        (SELECT p.project_id, c.patient_id, c.cell_type, i.image_type, q.quality
        FROM {project_name}_image i 
        LEFT JOIN {project_name}_patient p
        ON p.patient_id = i.patient_id
        LEFT JOIN {project_name}_cell c 
        ON i.cell_id = c.cell_id
        LEFT JOIN {project_name}_image_quality q
        ON i.image_id = q.image_id) t
    GROUP BY t.project_id, t.patient_id, t.cell_type, t.image_type, t.quality
    """
    data = pd.DataFrame(query_database(sql))
    data["quality"] = data["quality"].replace(
        {0: "Good", 1: "Bad", np.nan: "Unlabelled"}
    )
    data = data[data.image_type != "MIP"]
    data = data.pivot(
        index=["project_id", "patient_id", "cell_type"],
        columns=["image_type", "quality"],
        values="num_image",
    )
    data = data.fillna(0)
    data = data.astype(int)
    return data


def app():
    TitleRenderer("Labelled Data Overview").render()
    project_list = get_project_list()
    project_name = st.selectbox("Select Project", project_list)
    st.table(create_cell_metadata_table(f"{project_name}"))


if __name__ == "__main__":
    print(create_cell_metadata_table("2022_tomocube_sepsis"))
