#!/bin/bash

docker build -t web .

docker run --env-file .env -p 5000:5000 web "$@"
