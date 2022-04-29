#=============================================================================
# Build environment
FROM python:3.9.7-slim as build

# Install Poetry
RUN pip install --upgrade pip && pip install poetry==1.1.11
RUN mkdir /code
WORKDIR /code
# Create Poetry environment
COPY poetry.lock pyproject.toml /code/
RUN POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=true \
    poetry install

# =============================================================================
# Runtime environment
FROM python:3.9.7-slim as runtime

# Copy Poetry environment
COPY --from=build /code/.venv /code/.venv

# Update PATH
ENV PATH="/code/.venv/bin:$PATH"
COPY . /code
WORKDIR /code

CMD ["streamlit","run","main.py"]