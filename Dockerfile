FROM python:3.10.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      libjpeg62-turbo zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY main.py /app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/images /app/logs

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
