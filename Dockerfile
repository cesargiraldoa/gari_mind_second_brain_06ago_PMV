# Dockerfile_microsoft_repo_5ago25_OK (mínimo)
FROM python:3.10-bullseye

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Bogota \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ✅ unixODBC + repo MS + ODBC Driver 18
RUN apt-get update && apt-get install -y \
    curl gnupg apt-transport-https \
    unixodbc unixodbc-dev odbcinst \
    libgssapi-krb5-2 libkrb5-3 libcurl4 build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
CMD ["sh", "-c", "streamlit run main.py --server.port=$PORT --server.enableCORS=false --server.enableXsrfProtection=false"]
