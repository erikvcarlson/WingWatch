FROM ubuntu:22.04

#You will needto manually define the platform command when using a ARM Mac.The build command is: 
    
#docker build --platform linux/amd64 --pull --rm -f "Shiny_App/Dockerfile" -t wingwatch:latest "Shiny_App"


#FROM python:3.9

# Install dependencies

RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime 

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    cmake \ 
    libeigen3-dev \
    libgmp3-dev 

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /home/app

RUN chown app:app -R /home/app

USER app

RUN mkdir /tmp/users/

COPY basic-app/requirements.txt .
COPY WingWatch /home/app/WingWatch
#/Users/erikcarlson/Research/WingWatch/Shiny_App/Dockerfile

RUN pip3 install --no-cache-dir -r requirements.txt

COPY basic-app .

EXPOSE 8080

RUN echo "test" > test.txt

CMD ["python3","-m","uvicorn","app:app","--host","0.0.0.0","--port","8080","--root-path","/tmp/users"]