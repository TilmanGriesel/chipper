#!/bin/bash

docker build -t rest-cli .

docker run -i --env-file .env rest-cli "$@"
