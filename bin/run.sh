#!/bin/bash -l

function usage {
cat >&2 <<EOS
コンテナ起動コマンド

[usage]
 $0 [options] <CHAPTER>

[options]
 -h | --help:
   ヘルプを表示
 --sample:
   サンプルコードで起動
EOS
exit 1
}

PROJECT_ROOT="$(cd $(dirname $0)/..; pwd)"
cd "$PROJECT_ROOT"

ENV_PATH="${PROJECT_ROOT}/local.env"
IS_SAMPLE=
args=()
while [ "$#" != 0 ]; do
  case $1 in
    -h | --help      ) usage;;
    --sample         ) IS_SAMPLE=1;;
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

export $(cat $ENV_PATH | grep -v -e "^#")

# Docker build
docker build \
  --build-arg http_proxy=$https_proxy \
  --build-arg https_proxy=$https_proxy \
  --build-arg no_proxy=$NO_PROXY \
  -q \
  --rm \
  -f docker/fastapi/Dockerfile \
  -t fastapi-tutorial:latest \
  .

# Docker run
if [ -n "$IS_SAMPLE" ]; then
  LOCAL_APP_DIR="${PROJECT_ROOT}/tutorial/${CHAPTER}/sample"
else
  LOCAL_APP_DIR="${PROJECT_ROOT}/tutorial/${CHAPTER}/src"
fi
echo $LOCAL_APP_DIR
docker run \
  --rm \
  -ti \
  --network host \
  --env-file "$ENV_PATH" \
  -v ${LOCAL_APP_DIR}:/opt/app \
  fastapi-tutorial:latest \
  /entrypoint.sh