# Imagen base robusta y compatible con ODBC SQL Server
FROM python:3.10-bullseye

# Variables de entorno
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Bogota

# Instalación de dependencias del sistema necesarias para pyodbc y SQL Server
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    libcurl4 \
    libkrb5-3 \
    libgssapi-krb5-2 \
    curl \
    gnupg \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    && apt-get clean

# Crear carpeta de trabajo
WORKDIR /app

# Copiar requirements y código
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Comando por defecto
CMD ["streamlit", "run", "main.py", "--server.port=10000", "--server.enableCORS=false"]



