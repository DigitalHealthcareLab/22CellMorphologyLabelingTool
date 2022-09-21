# Tomocube image labeller

- Author: MinDong Sung
- Date: 2022-04-27

---

## Objective

- The image quality is important to decide whether the image was included in dataset or not.

## Prerequisite
- [Docker](https://docs.docker.com/)
- [Docker-compose](https://docs.docker.com/compose/)
- python 3.9
- poetry
- Images should uploaded on google drive.
- Images would be fetches via google drive API.

## Preprocess
- Install all dependencies with [poetry](https://python-poetry.org/)
```
poetry install && poetry 
```
## Process
- run streamlit 
```
streamlit main.py
```

## Docker deploy
- deply with docker-compose
- port could be changed with changing `docker-compose.yaml` file
```
docker-compose up -d
```

## Screenshot
<img width="1792" alt="image" src="https://user-images.githubusercontent.com/52244362/165658149-8861e39e-02c8-4349-9dba-625723c3ad75.png">
