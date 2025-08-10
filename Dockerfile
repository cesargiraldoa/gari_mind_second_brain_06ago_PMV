FROM python:3.10-bullseye

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Bogota \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 🔧 Dependencias del sistema + Repo Microsoft + ODBC Driver 18
RUN apt-get update && apt-get install -y \
    curl gnupg2 apt-transport-https software-properties-common \
    unixodbc unixodbc-dev odbcinst \
    libgssapi-krb5-2 libkrb5-3 libcurl4 \
    build-essential gcc g++ \
 && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
 && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/microsoft-prod.list \
 && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# ▶️ Arranque (Render usa $PORT)
CMD ["sh","-c","streamlit run dashboard.py --server.port=${PORT:-10000} --server.enableCORS=false --server.enableXsrfProtection=false"]
