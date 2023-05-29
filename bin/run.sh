#!/bin/bash -l

function usage {
cat >&2 <<EOS
コンテナ起動コマンド

[usage]
 $0 <CHAPTER> [options]

[options]
 -h | --help:
   ヘルプを表示
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
args=()
while [ "$#" != 0 ]; do
  case $1 in
    -h | --help      ) usage;;
    --sample         ) IS_SAMPLE=1;;
    -m | --mode           ) shift; MODE="$1";;
    -* | --*         ) echo "$1 : 不正なオプションです" >&2; exit 1;;
    *                ) args+=("$1");;
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
  --build-arg host_uid=$(id -u) \
  --build-arg host_gid=$(id -g) \
  --rm \
  -f docker/app/Dockerfile \
  -t fastapi-tutorial:latest \
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
  CMD="jupyter lab --ip=* --no-browser --notebook-dir /opt/app/"
else
  CMD="supervisord -c /etc/supervisor/supervisord.conf"
fi
echo $CMD
docker run \
  --rm \
  -ti \
  --network host \
  --env-file "$ENV_PATH" \
  -e "DB_NAME=$(echo $CHAPTER | sed -e 's/[^a-zA-Z0-9]/_/g')" \
  --user="$(id -u):$(id -g)" \
  -w /opt/app \
  -v ${LOCAL_APP_DIR}:/opt/app \
  fastapi-tutorial:latest \
  $CMD