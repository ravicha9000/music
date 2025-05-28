# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY stock_analyzer_webapp/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire web application code into the container at /app
COPY stock_analyzer_webapp/ .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# Remove ENV FLASK_DEBUG=1 for a more production-like setup, 
# or keep it if debugging within Docker is desired initially.
# For this task, let's keep it simple for now.
ENV FLASK_DEBUG=1 

# Run app.py when the container launches
CMD ["flask", "run"]
