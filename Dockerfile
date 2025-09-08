FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (default from env, but fallback 8000)
EXPOSE ${APP_PORT:-8080}

# Use environment variables in CMD
CMD ["sh", "-c", "uvicorn main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000} --log-level ${LOG_LEVEL:-info}"]
