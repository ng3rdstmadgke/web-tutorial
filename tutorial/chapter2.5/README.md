[Chapter2.5] SQLAlchemyを利用したデータベースの操作
--
[top](../../README.md)

# Note

このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter2/src` をルートディレクトリとして解説します。  
chapter2.5では、chapter2で学んだDBの操作をPythonからSQLAlchemyを利用して行う方法を学びます。

# ■ mysqlを起動しましょう

```bash
./bin/mysql.sh
```

# ■ Pythonからデータベースを触ってみる (SQLAlchemy)

[SQLAlchemy](https://www.sqlalchemy.org/)

## データベースの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter2.5 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "DROP DATABASE IF EXISTS chapter2_5"
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter2_5"

# 開発用shellからログアウト
exit
```

## JupyterLab起動

```bash
./bin/run.sh chapter2.5 --mode jupyter
```

jupyter起動時に表示されるURL( http://localhost:8889/lab?token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx )にブラウザでアクセスしてください。

`tutorial/chapter2.5/sample/sqlalchemy_tutorial.ipynb` の実装を参考に、SQLAlchemyを利用してPythonからデータベースを操作してみましょう。