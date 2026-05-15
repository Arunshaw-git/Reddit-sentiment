# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AGENT_PORT=8080

# Expose the port
EXPOSE 8080

# Command to run the FastAPI service
CMD ["python", "main.py"]
