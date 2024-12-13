# Use Python base image
FROM python:3.11-slim

# Set working directory inside the container
RUN mkdir -p /app/senderX
WORKDIR /app/senderX

# Copy the current directory contents into the container
COPY . /app/senderX

# Install dependencies
RUN pip install --no-cache-dir -r /app/senderX/requirements.txt

# Expose the port (optional)
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
