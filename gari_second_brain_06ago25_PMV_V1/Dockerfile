# Imagen base funcional validada (Abraham)
FROM python:3.10-bullseye

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Bogota

RUN apt-get update && apt-get install -y \
    gcc g++ curl gnupg \
    libssl-dev libffi-dev \
    libpq-dev unixodbc unixodbc-dev \
    libcurl4 libkrb5-3 libgssapi-krb5-2

# Instala el driver ODBC 18 para SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]