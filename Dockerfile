# choosing a base image
FROM python:3.13.11-slim

# Setting the working directory inside the container
WORKDIR /app
# were just calling our working directory app, ic could be anything tho

# Create a non-root user early so subsequent COPY/RUN steps can use it
RUN useradd --create-home appuser

# Copying the requirements file to the working directory and installing dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying rest of the code
COPY . .

# Ensure appuser owns application files and switch to it
RUN chown -R appuser:appuser /app
USER appuser

# Expose the PORT
EXPOSE 8000

# Add a health check to monitor container status
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/ || exit 1

# Command to start the FASTAPI application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT