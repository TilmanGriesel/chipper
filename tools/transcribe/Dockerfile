FROM ubuntu:22.04

ARG VERSION=latest
ENV APP_VERSION=$VERSION

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    sudo \
    python3.9 \
    python3-distutils \
    python3-pip \
    ffmpeg

RUN pip install --upgrade pip

RUN pip install -U openai-whisper

WORKDIR /app

CMD ["whisper"]
