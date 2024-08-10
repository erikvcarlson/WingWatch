#FROM amd64/ubuntu:22.04
FROM ubuntu:22.04

# Install dependencies

RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime 

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    cmake \ 
    libeigen3-dev \
    libgmp3-dev \
    libx11-dev \
    libxext-dev \
    libxrender-dev\
    libxinerama-dev \ 
    libxi-dev \ 
    libxrandr-dev \ 
    libxcursor-dev \
    libxtst-dev \
    python3-tk

# Make port 80 available to the world outside this container
# EXPOSE 80
# Add other dependencies here
# Copy your application code
COPY . /app


# Set the working directory
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Set a default command (optional)
#CMD ["bash", "-c", "while true; do sleep 1000; done"]

CMD ["python3", "application.py"]