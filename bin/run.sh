#!/bin/bash -l

function usage {
cat >&2 <<EOS
コンテナ起動コマンド

[usage]
 $0 <CHAPTER> [options]

[options]
 -h | --help:
   ヘルプを表示
 -u | --uid <USER_ID>:
   ユーザーidを指定
 -g | --gid <GROUP_ID>:
   グループidを指定
 --sample:
   サンプルコードで起動
 -m | --mode <MODE>:
  起動モードを指定
  MODE:
    app
      fastapiを起動 (default)
    shell
      コンテナにshellでログイン
    jupyter
      JupyterLabを起動

[example]
 chapter1 で見本のアプリを起動する
   $0 chapter1 --sample
 chapter1 でshellを起動する
   $0 chapter1 --mode shell
 chapter1 でJupyterLabを起動する
   $0 chapter1 --mode jupyter
EOS
exit 1
}

PROJECT_ROOT="$(cd $(dirname $0)/..; pwd)"
cd "$PROJECT_ROOT"

ENV_PATH="${PROJECT_ROOT}/local.env"
IS_SAMPLE=
MODE="app"
USER_ID=$(id -u)
GROUP_ID=$(id -g)
args=()
while [ "$#" != 0 ]; do
  case $1 in
    -h | --help ) usage;;
    -u | --uid  ) shift; USER_ID=$1 ;;
    -g | --gid  ) shift; GROUP_ID=$1 ;;
    --sample    ) IS_SAMPLE=1 ;;
    -m | --mode ) shift; MODE="$1" ;;
    -* | --*    ) echo "$1 : 不正なオプションです" >&2; exit 1 ;;
    *           ) args+=("$1") ;;
  esac
  shift
done

[ "${#args[@]}" != 1 ] && usage

CHAPTER=${args[0]}
if [ ! -d "${PROJECT_ROOT}/tutorial/${CHAPTER}" ]; then
  echo "指定されたチャプター( ${CHAPTER} )は存在しません。下記いずれかのチャプターを指定してください。" >&2
  ls tutorial >&2
  exit 1
fi

if [ "$MODE" != "app" -a "$MODE" != "shell" -a $MODE != "jupyter" ]; then
  echo "--mode には app, shell, jupyterのいずれかを指定してください" >&2
  exit 1
fi

export $(cat $ENV_PATH | grep -v -e "^ *#")

# Docker build
export DOCKER_BUILDKIT=1
docker build \
  --build-arg http_proxy=$https_proxy \
  --build-arg https_proxy=$https_proxy \
  --build-arg no_proxy=$NO_PROXY \
  --build-arg host_uid=$USER_ID \
  --build-arg host_gid=$GROUP_ID \
  --rm \
  -f docker/app/Dockerfile \
  -t web-tutorial:latest \
  .

# Docker run
if [ -n "$IS_SAMPLE" ]; then
  LOCAL_APP_DIR="${PROJECT_ROOT}/tutorial/${CHAPTER}/sample"
else
  LOCAL_APP_DIR="${PROJECT_ROOT}/tutorial/${CHAPTER}/src"
fi

if [ "$MODE" = "shell" ]; then
  CMD="/bin/bash"
elif [ "$MODE" = "jupyter" ]; then
  CMD="jupyter lab --ip=* --port 8892 --no-browser --notebook-dir /opt/app/"
  CONTAINER_NAME="web-tutorial-jupyter"
  OPTIONS="-p 8892:8892 --name $CONTAINER_NAME"
else
  CMD="supervisord -c /etc/supervisor/supervisord.conf"
  CONTAINER_NAME="web-tutorial-app"
  OPTIONS="-p 8018:8018 -p 3000:3000 -p 24678:24678 --name $CONTAINER_NAME"
fi

if [ -n "$CONTAINER_NAME" ]; then
  docker rm -f $CONTAINER_NAME
fi

NETWORK_NAME="br-web-tutorial"
NETWORK_EXISTS="$(docker network inspect $NETWORK_NAME >/dev/null 2>&1; echo $?)"
if [ "$NETWORK_EXISTS" = 1 ]; then
  docker network create --driver bridge --subnet "10.29.10.0/24" $NETWORK_NAME
fi

docker run \
  $OPTIONS \
  --rm \
  -ti \
  --network $NETWORK_NAME \
  --env-file "$ENV_PATH" \
  -e "DB_NAME=$(echo $CHAPTER | sed -e 's/[^a-zA-Z0-9]/_/g')" \
  --user="$USER_ID:$GROUP_ID" \
  -w /opt/app \
  -v ${LOCAL_APP_DIR}:/opt/app \
  web-tutorial:latest \
  $CMD