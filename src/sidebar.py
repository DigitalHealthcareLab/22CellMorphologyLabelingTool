from src.database import query_database


def get_project_list():
    data_list = query_database("SELECT project_id, name FROM project")
    return [data["name"] for data in data_list]


def get_patient_list(project_name: str):
    data_list = query_database(f"SELECT patient_id FROM {project_name}_patient")
    return [data["patient_id"] for data in data_list]


def get_cell_type(project_name: str):
    data_list = query_database(
        f"SELECT distinct(cell_type) FROM {project_name}_cell ORDER BY cell_type"
    )
    return [data["cell_type"] for data in data_list]


def get_cell_number(project_name: str, patient_id: int, cell_type: str):
    data_list = query_database(
        f"SELECT cell_number FROM {project_name}_cell WHERE cell_type = '{cell_type}' AND patient_id = {patient_id} ORDER BY cell_number"
    )
    return [data["cell_number"] for data in data_list]
