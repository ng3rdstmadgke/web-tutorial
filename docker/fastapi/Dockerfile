FROM python:3.8.12-slim-bullseye

ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG host_uid
ARG host_gid

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV NO_PROXY=$no_proxy

RUN apt update && \
    apt install -y locales curl default-mysql-client jq unzip groff less vim fzf net-tools iputils-ping sudo tmux

# ロケール設定
RUN echo 'ja_JP.UTF-8 UTF-8' >> /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ja_JP.UTF-8
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# ユーザー作成
RUN groupadd -g $host_gid app && \
    useradd -u $host_uid -o -m -g $host_gid -s /bin/bash app && \
    echo "app ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/app

COPY docker/fastapi/.private_bashrc /home/app/.private_bashrc
RUN echo "source ~/.private_bashrc" >> /home/app/.bashrc

# Pythonライブラリインストール
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Jupyter Labインストール
RUN pip install jupyterlab

RUN mkdir -p /opt/app
WORKDIR /opt/app

COPY docker/fastapi/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]