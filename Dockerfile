# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy project files
COPY Code/ /app
COPY data/ /data

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8000

# Start the application
CMD ["python", "app.py"]
