FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for database..."\n\
sleep 10\n\
echo "Running database migrations..."\n\
alembic upgrade head\n\
echo "Starting application..."\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]