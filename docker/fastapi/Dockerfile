FROM python:3.8.12-slim-bullseye

ARG http_proxy
ARG https_proxy
ARG no_proxy

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV NO_PROXY=$no_proxy

RUN apt update && \
    apt install -y locales && \
    apt upgrade -y

RUN echo 'ja_JP.UTF-8 UTF-8' >> /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ja_JP.UTF-8

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN mkdir -p /opt/app
WORKDIR /opt/app

COPY docker/fastapi/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]