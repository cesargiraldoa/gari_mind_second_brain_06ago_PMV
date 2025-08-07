FROM python:3.10-bullseye

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Bogota

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

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "main.py", "--server.port=10000", "--server.enableCORS=false"]
