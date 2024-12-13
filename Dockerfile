# Use the official Python image from the DockerHub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /senderX

# Copy the requirements.txt into the container
COPY requirements.txt /senderX/

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /senderX/

# Expose the port that the app will run on
EXPOSE 8000

# Set the environment variable for the Django secret key
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

# Run the Django application when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
