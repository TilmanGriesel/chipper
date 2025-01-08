FROM ubuntu:22.04

ARG VERSION=latest
ENV APP_VERSION=$VERSION

ARG BUILD_NUM=0
ENV APP_BUILD_NUM=$BUILD_NUM

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
