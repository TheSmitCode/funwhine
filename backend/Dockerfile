# Dockerfile - simple Python app image
FROM python:3.12-slim

WORKDIR /code

# system deps needed to build some wheels (e.g., bcrypt, asyncpg if added)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt /code/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy project
COPY . /code

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
