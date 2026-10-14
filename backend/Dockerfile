FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt requirements.lock.txt ./
RUN pip install -r requirements.txt -c requirements.lock.txt
COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations

FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt -c requirements.lock.txt
COPY tests ./tests
COPY pyproject.toml .
CMD ["pytest", "-q"]

FROM base AS runtime
RUN useradd --create-home nova
USER nova
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m app.seed && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
