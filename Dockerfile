# Use Python 3.12.7 Bookworm as Base Image.
FROM python:3.12.7-bookworm

# Set working dir
WORKDIR /ausonia_bot

# Copy requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Firefox
RUN apt-get update && apt-get upgrade -y
RUN apt-get install flatpak -y
RUN flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
RUN flatpak install flathub org.mozilla.firefox -y