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
    -* | --*         ) echo "$1 : 不正なオプションです" >&2; exit 1;;
    *             ) args+=("$1");;
  esac
  shift
done

[ "${#args[@]}" != 0 ] && usage

set -e
export $(cat $ENV_PATH | grep -v -e "^ *#")

# docker build
docker build \
  -q \
  --rm \
  -f docker/mysql/Dockerfile \
  -t fastapi-tutorial-mysql:latest \
  .

# docker run
docker rm -f fastapi-tutorial-mysql

docker run \
  -d \
  --rm \
  --network host \
  --name fastapi-tutorial-mysql \
  -e MYSQL_USER=$DB_USER \
  -e MYSQL_PASSWORD=$DB_PASSWORD \
  -e MYSQL_DATABASE=app \
  -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD \
  fastapi-tutorial-mysql:latest

docker run \
  --rm \
  --name fastapi-tutorial-mysql-check \
  --env-file "$ENV_PATH" \
  --network host \
  fastapi-tutorial-mysql:latest \
  /check.sh