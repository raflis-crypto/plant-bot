FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
CMD ["sh", "-c", "echo Starting on port $PORT && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
