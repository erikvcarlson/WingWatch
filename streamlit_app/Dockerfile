# app/Dockerfile
FROM ubuntu:22.04

#FROM python:3.9

# Install dependencies

RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime 

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip 

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /home/app

RUN chown app:app -R /home/app

USER app


COPY requirements.txt .
COPY WingWatch /home/app/WingWatch

RUN pip3 install --no-cache-dir -r requirements.txt

RUN pip3 install streamlit


EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]