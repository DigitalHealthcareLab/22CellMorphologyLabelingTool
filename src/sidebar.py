from src.database import query_database


def get_project_list():
    data_list = query_database("Show tables")
    return [
        data["Tables_in_tomocube"].replace("_patient", "")
        for data in data_list
        if "patient" in data["Tables_in_tomocube"]
    ]


def get_patient_list(project_name: str):
    data_list = query_database(f"SELECT patient_id FROM {project_name}_patient")
    return [data["patient_id"] for data in data_list]


def get_cell_type(
    project_name: str, patient_id: int, filter_labeled: bool = False
):
    sql = (
        f"SELECT distinct(cell_type) FROM {project_name}_cell WHERE patient_id = {patient_id} AND cell_id IN (SELECT distinct(cell_id) FROM {project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {project_name}_image_quality)) ORDER BY cell_type"
        if filter_labeled
        else f"SELECT distinct(cell_type) FROM {project_name}_cell WHERE patient_id = {patient_id} ORDER BY cell_type"
    )

    data_list = query_database(sql)
    return [data["cell_type"] for data in data_list]


def get_cell_number(
    project_name: str,
    patient_id: int,
    cell_type: str,
    filter_labeled: bool = False,
):
    sql = (
        f"SELECT distinct(cell_number) FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND patient_id = {patient_id} AND cell_id IN (SELECT distinct(cell_id) FROM {project_name}_image WHERE image_id NOT IN (SELECT image_id FROM {project_name}_image_quality)) ORDER BY cell_number"
        if filter_labeled
        else f"SELECT cell_number FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND patient_id = {patient_id} ORDER BY cell_number"
    )

    data_list = query_database(sql)
    return [data["cell_number"] for data in data_list]


if __name__ == "__main__":
    print(get_project_list())
