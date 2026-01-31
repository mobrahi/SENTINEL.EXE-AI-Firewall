# Use the official lightweight Python image
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Set the working directory in the container
WORKDIR /app

# Copy local code to the container image
COPY . ./

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup using gunicorn
# We bind to the port defined by the Cloud Run environment variable
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
