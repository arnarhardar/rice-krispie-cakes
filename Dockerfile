# Use an official Python runtime as a base image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy your project files to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]
