# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY api_server/app.py /app/app.py
COPY init_data.py /app/init_data.py
COPY templates/ /app/templates/
COPY settings.py /app/settings.py

# Install the required Python dependencies
RUN pip install --upgrade pip
RUN pip install flask fastapi spacy redis pymongo
RUN pip install spacy
RUN python -m spacy download en_core_web_sm

# Expose the port that Flask will run on
EXPOSE 5000

# Set the default command to run the app
CMD ["python", "app.py"]
