FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    cmake \ 
    libeigen3-dev \
    libgmp3-dev \
    qt6-base-dev \
    libx11-xcb1 \
    libxcb1 \
    libx11-dev

# Make port 80 available to the world outside this container
# EXPOSE 80
# Add other dependencies here
# Copy your application code
COPY . /app

# Set the working directory
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt
RUN pip3 install PySide6


# Define the entry point
CMD ["python3", "application.py"]
