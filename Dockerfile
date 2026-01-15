FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application file
COPY app.py .

# Install dependencies
RUN pip install --no-cache-dir flask redis

# Expose port 5000
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Run the application
CMD ["python", "app.py"]
