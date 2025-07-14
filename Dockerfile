FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "job_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
