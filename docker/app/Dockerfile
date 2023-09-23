FROM python:3.10-slim-bookworm

ARG http_proxy
ARG https_proxy
ARG no_proxy
ARG host_uid
ARG host_gid

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV NO_PROXY=$no_proxy

RUN apt-get update && \
    apt-get install -y locales curl default-mysql-client jq unzip groff less vim fzf net-tools iputils-ping sudo tmux gcc

# ロケール設定
RUN echo 'ja_JP.UTF-8 UTF-8' >> /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ja_JP.UTF-8
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# ユーザー作成
RUN groupadd -g $host_gid app && \
    useradd -u $host_uid -o -m -g $host_gid -s /bin/bash app && \
    echo "app ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/app

COPY docker/app/.private_bashrc /home/app/.private_bashrc
RUN echo "source ~/.private_bashrc" >> /home/app/.bashrc

# Jupyter Labインストール
RUN pip install --upgrade pip && \
    pip install jupyterlab

# supervisorインストール
RUN pip install supervisor

# nodejs v18.x インストール
# https://github.com/nodesource/distributions#installation-instructions
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install nodejs -y

# npm v10.x インストール
RUN npm install -g npm@^10.0.0

# pnpm install
#USER app
#RUN curl -fsSL https://get.pnpm.io/install.sh | bash -
#USER root

# Pythonライブラリインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# supervisorの設定ファイルとエントリーポイント
COPY docker/app/supervisor /etc/supervisor
COPY docker/app/entrypoint-api.sh /entrypoint-api.sh
COPY docker/app/entrypoint-front.sh /entrypoint-front.sh
RUN chmod +x /entrypoint-*.sh

# importの起点となるパスを環境変数として定義
ENV PYTHONPATH=/opt/app/api

ENTRYPOINT []

CMD ["/entrypoint.sh"]