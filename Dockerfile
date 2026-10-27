# choosing a base image
FROM python:3.13.11-slim

# Setting the working directory inside the container
WORKDIR /app
# were just calling our working directory app, ic could be anything tho

# Copying the requirements file to the working directory and installing dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying rest of the code
COPY . .

# Run the application as a non-root user
RUN useradd --create-home --uid 10001 appuser
USER 10001:10001

# Expose the PORT
EXPOSE 8000

# Command to start the FASTAPI application
CMD uvicorn main:app --host 0.0.0.0 --port $PORT