# Use a lightweight Python image
FROM python:3.11-slim

# Install system dependencies for Pygame
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the game code
COPY . .

# Set environment variables (API Key should be passed at runtime)
ENV PYTHONUNBUFFERED=1

# Run the game
CMD ["python", "main.py"]