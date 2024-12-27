#!/bin/bash

docker build -t api .

docker run --env-file .env -p 8000:8000  api
