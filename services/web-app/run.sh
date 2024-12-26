#!/bin/bash

docker build -t web-app .

docker run --env-file .env -p 5000:5000 web-app "$@"
