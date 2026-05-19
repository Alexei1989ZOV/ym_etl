FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код проекта
COPY app ./app

# VCS метка
ARG VCS_REF
LABEL org.opencontainers.image.revision=$VCS_REF

# Точка входа для Airflow DockerOperator
ENTRYPOINT ["python"]