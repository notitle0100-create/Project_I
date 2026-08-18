FROM python:3.12.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY pyproject.toml README.md alembic.ini ./
COPY alembic ./alembic
COPY src ./src

RUN python -m pip install --no-cache-dir .

USER app

EXPOSE 8000

CMD ["uvicorn", "seoul_mens_daily_edit.main:app", "--host", "0.0.0.0", "--port", "8000"]
