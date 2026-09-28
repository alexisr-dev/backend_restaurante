# Se construye desde la raiz del proyecto porque necesita schema.sql,
# que vive fuera de esta carpeta:
#   docker build -f backend_restaurante/Dockerfile .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend_restaurante/requirements.txt .
RUN pip install -r requirements.txt

COPY backend_restaurante/ .

# La migracion inicial lo busca en el directorio padre de BASE_DIR.
COPY schema.sql /schema.sql

EXPOSE 8010

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8010", "--workers", "3"]
