# Dockerfile

FROM python:3.12-slim

# Avoid .pyc and make logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (optional, minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose port inside container
EXPOSE 8000

# Start FastAPI via uvicorn
# If your file is main.py, change to: main:app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
