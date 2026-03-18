FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .

# Install the required Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

# Copy source code
COPY services/intent_recognition/ .

EXPOSE 5004

CMD ["python", "intent.py"]