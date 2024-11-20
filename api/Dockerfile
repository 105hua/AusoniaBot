# Use Python 3.12.7 Bookworm as Base Image.
FROM python:3.12.7-bookworm

# Set working dir
WORKDIR /ausonia_api

# Copy requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt