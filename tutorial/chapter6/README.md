[Chapter6] APIテストを実装してみよう
--
[top](../../README.md)

# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter6/src` をルートディレクトリとして解説します。

chapter6では、これまでに実装したAPIのテストを実装していきましょう。

# ■ mysqlを起動しましょう

※ 起動していない場合のみ

```bash
./bin/mysql.sh
```

# ■ テーブルの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter6 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter6"

# マイグレーション
alembic upgrade head
```
