# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter4/src` をルートディレクトリとして解説します。


# ■ テーブルの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter4 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter4"

# マイグレーション
alembic upgrade head
```