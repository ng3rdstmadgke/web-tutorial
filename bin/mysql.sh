#!/bin/bash
shopt -s expand_aliases
[ -f "$HOME/.bashrc" ] && source $HOME/.bashrc

function usage {
cat >&2 <<EOS
mysqlコンテナ起動コマンド

[usage]
 $0 [options]

[options]
 -h | --help:
   ヘルプを表示
EOS
exit 1
}

PROJECT_ROOT="$(cd $(dirname $0)/..; pwd)"
cd "$PROJECT_ROOT"

ENV_PATH="${PROJECT_ROOT}/local.env"
args=()
while [ "$#" != 0 ]; do
  case $1 in
    -h | --help   ) usage;;
    -* | --*      ) echo "$1 : 不正なオプションです" >&2; exit 1;;
    *             ) args+=("$1");;
  esac
  shift
done

[ "${#args[@]}" != 0 ] && usage

set -e
export $(cat $ENV_PATH | grep -v -e "^ *#")

# docker build
export DOCKER_BUILDKIT=1
docker build \
  --rm \
  -f docker/mysql/Dockerfile \
  -t web-tutorial-mysql:latest \
  .

# docker run
docker rm -f web-tutorial-mysql

NETWORK_NAME="br-web-tutorial"
NETWORK_EXISTS="$(docker network inspect $NETWORK_NAME >/dev/null 2>&1; echo $?)"
if [ "$NETWORK_EXISTS" = 1 ]; then
  docker network create --driver bridge --subnet "10.29.10.0/24" $NETWORK_NAME
fi

docker run \
  -d \
  --rm \
  --network $NETWORK_NAME \
  --ip=10.29.10.100 \
  --name web-tutorial-mysql \
  -e MYSQL_ROOT_PASSWORD=$DB_PASSWORD \
  web-tutorial-mysql:latest

docker run \
  --rm \
  --name web-tutorial-mysql-check \
  --env-file "$ENV_PATH" \
  --network $NETWORK_NAME \
  web-tutorial-mysql:latest \
  /check.sh