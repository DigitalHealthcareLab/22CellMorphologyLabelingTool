#=============================================================================
# Build environment
FROM python:3.9.7-slim as build

# Install Poetry
RUN pip install poetry

# Create Poetry environment
COPY poetry.lock pyproject.toml 
RUN POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=true \
    poetry install

# =============================================================================
# Runtime environment
FROM python:3.7-slim as runtime

# Copy Poetry environment
COPY --from=build .venv /code/.venv

# Update PATH
ENV PATH="/code/.venv/bin:$PATH"
COPY . /code
WORKDIR /code

CMD ["streamlit","run","main.py"]