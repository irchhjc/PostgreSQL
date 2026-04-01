FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

COPY sql ./sql
COPY scripts ./scripts
COPY data ./data

CMD ["python", "scripts/load_data.py"]