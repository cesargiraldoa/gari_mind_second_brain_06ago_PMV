FROM python:3.10-bullseye

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=America/Bogota \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Render/Cloud: respeta $PORT
CMD ["sh", "-c", "streamlit run main.py --server.port=$PORT --server.enableCORS=false --server.enableXsrfProtection=false"]
