# app/Dockerfile
FROM ubuntu:22.04

#FROM python:3.9

# Install dependencies

RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime 

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /home/app

RUN chown app:app -R /home/app

USER app


COPY requirements.txt .
COPY WingWatch /home/app/WingWatch
COPY app.py /home/app/
COPY st_local_storage.py /home/app
RUN pip3 install --no-cache-dir -r requirements.txt
#RUN git clone https://github.com/toolittlecakes/streamlit_js


ENV PATH=${PATH}:/home/app/.local/bin/ 

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]