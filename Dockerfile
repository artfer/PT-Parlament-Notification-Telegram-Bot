# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including cron
RUN apt-get update && apt-get install -y cron

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY src/ ./src/

# Declare a volume for persistent data (e.g., the last_vote_day.txt file)
VOLUME /app/data

# Create a cron job file
RUN echo "0 22 * * * cd /app && /usr/local/bin/python -m src.main >> /proc/1/fd/1 2>> /proc/1/fd/2" > /etc/cron.d/parliament-cron

# Give execution rights on the cron job file
RUN chmod 0644 /etc/cron.d/parliament-cron

# Apply the cron job
RUN crontab /etc/cron.d/parliament-cron

# Create an empty log file for cron and give it the right permissions
RUN touch /var/log/cron.log

# Run the command on container startup
# Start the cron daemon in the foreground
CMD cron && tail -f /var/log/cron.log