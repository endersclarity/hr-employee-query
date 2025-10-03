FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck, postgresql-client for database operations, and bash
RUN apt-get update && apt-get install -y curl postgresql-client bash && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
