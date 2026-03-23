# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

COPY requirements.txt .

# Install the required Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

# Copy source code
COPY services/api_server/ .

# Expose the port that Flask will run on
EXPOSE 5000

# Set the default command to run the app
CMD ["python", "app.py"]
