FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
set -e\n\
set -x\n\
echo "Waiting for database..."\n\
while ! nc -z db 5432; do\n\
  sleep 1\n\
done\n\
echo "Database is ready!"\n\
\n\
echo "Running database migrations..."\n\
alembic upgrade head\n\
\n\
echo "Importing initial data..."\n\
python -m app.scripts.import_datas\n\
\n\
echo "Starting application..."\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

#CMD   alembic revision --autogenerate -m "init" && alembic upgrade head && python -m app.scripts.import_datas && uvicorn app.main:app --host 0.0.0.0 --port 8000
CMD ["/app/start.sh"]