#!/bin/bash

docker build -t rest-api .

docker run --env-file .env -p 8000:8000 rest-api --stats
