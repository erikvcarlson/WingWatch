#!/bin/bash

docker rm -f $(docker ps -aq)

pytest test_intro.py
rsync -avz --ignore-existing --delete WingWatch Shiny_App
rsync -avz requirements.txt Shiny_App/basic-app
docker build --platform linux/amd64 --pull --rm -f "Shiny_App/Dockerfile" -t wingwatch:latest "Shiny_App"
docker run --name wingwatch_container -d -p 8080:8080/tcp wingwatch:latest

# Attach a shell to the running container
docker exec -it wingwatch_container /bin/bash
