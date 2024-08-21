# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
# COPY requirements.txt .
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Copy the rest of the application code
# COPY . .
ENV project_name projects/[PROJECT_NAME]
ENV webhook_url [SLACK_WEBHOOK_URL]

# Command to run the application
CMD ["python", "app.py"]
