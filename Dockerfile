# Se construye desde la raiz de este repo (ya standalone, no un
# subdirectorio de monorepo):
#   docker build -t backend_restaurante .
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# La migracion inicial busca schema.sql en el directorio padre de BASE_DIR
# (apps/usuarios/migrations/0001_initial.py). BASE_DIR = Path(__file__)
# .resolve().parents[2] desde config/settings/base.py; con WORKDIR /app eso
# resuelve a /app. Por eso el archivo debe quedar en /schema.sql, un nivel
# por encima de /app, y se copia aparte, al margen del COPY . . de arriba.
COPY schema.sql /schema.sql

EXPOSE 8010

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8010", "--workers", "3"]
