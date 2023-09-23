#!/bin/bash

# set -e : コマンドのreturn_codeが0以外だったら終了
# set -x : デバッグログを表示
set -ex

# このスクリプトの絶対パス
SCRIPT_DIR=$(cd $(dirname $0); pwd)

# プロジェクトルートの絶対パス
ROOT_DIR=$(cd $(dirname $0)/..; pwd)

cd $ROOT_DIR

# データベースを削除
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "DROP DATABASE IF EXISTS $DB_NAME"

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS $DB_NAME"

# マイグレーション
alembic upgrade head

# 初期ユーザー作成
PASSWD="admin"
python api/manage.py create-user sys_admin -r SYSTEM_ADMIN -p $PASSWD
python api/manage.py create-user loc_admin -r LOCATION_ADMIN -p $PASSWD
python api/manage.py create-user loc_operator -r LOCATION_OPERATOR -p $PASSWD