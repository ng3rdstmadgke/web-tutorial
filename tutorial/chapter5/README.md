# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter5/src` をルートディレクトリとして解説します。


# ■ テーブルの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter5 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter5"

# マイグレーション
alembic upgrade head
```


# ■ ログインが必要なアイテムのCRUDを実装してみましょう

## アイテムの新規作成
## アイテムの一覧
## アイテムの更新
## アイテムの削除
