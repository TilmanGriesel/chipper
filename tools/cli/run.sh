#!/bin/bash

docker build -t rest-cli .

docker run --rm --name chipper-cli -i --env-file .env rest-cli "$@"
