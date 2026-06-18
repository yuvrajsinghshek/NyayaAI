FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p ai/data/chroma_db

ENV PYTHONPATH=/app
ENV PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "PYTHONPATH=/app python ai/ingest/ingest_pipeline.py && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
