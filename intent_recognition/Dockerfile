FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY intent_recognition/intent.py /app/intent.py
COPY settings.py /app/settings.py

# Install the required Python dependencies
RUN pip install --upgrade pip
RUN pip install flask fastapi spacy redis pymongo
RUN pip install spacy
RUN python -m spacy download en_core_web_sm

EXPOSE 5004

CMD ["python", "intent.py"]