# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter2/src` をルートディレクトリとして解説します。

# ■ SQLを実行してみましょう

開発コンテナのshellを起動

```bash
./bin/run.sh chapter2 --sample --mode shell
```

MySQLにログイン

```bash
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT
```

データベースを作成

```sql
-- データベースの新規作成
CREATE DATABASE IF NOT EXISTS chapter2;

-- データベース一覧を表示
SHOW DATABASES;

-- 利用するデータベースを選択
USE chapter2
```

テーブルを作成

```sql
-- テーブルを作成
CREATE TABLE IF NOT EXISTS chapter2.users (
    id int NOT NULL AUTO_INCREMENT,
    name varchar(64) NOT NULL,
    age int,
    PRIMARY KEY (id),
    UNIQUE KEY (name)
);

-- テーブル一覧を表示
SHOW TABLES;

-- テーブル定義を表示
DESC users;
```

データの操作

```sql
-- データの挿入
INSERT INTO chapter2.users (name, age) VALUES ("yamada", 20);
INSERT INTO chapter2.users (name, age) VALUES ("sato", 30);
INSERT INTO chapter2.users (name, age) VALUES ("suzuki", 40);
INSERT INTO chapter2.users (name, age) VALUES ("tanaka", 50);

-- データの取得
SELECT * FROM chapter2.users;

-- 条件を指定してデータを取得
SELECT * FROM chapter2.users WHERE age >= 30;

-- 件数を指定してデータを取得
SELECT id, name FROM chapter2.users LIMIT 1;

-- データの変更
UPDATE chapter2.users SET name='midorikawa', age=32 WHERE name='sato';

-- データの削除
DELETE FROM chapter2.users WHERE id=3;
```

【発展】リレーション

```sql
-- usersに紐づくitemsテーブルを追加
CREATE TABLE IF NOT EXISTS chapter2.items (
    id int NOT NULL AUTO_INCREMENT,
    user_id int NOT NULL,
    title varchar(64) NOT NULL,
    content varchar(128) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY fk_user (user_id) REFERENCES users (id)
);

-- itemsを追加
INSERT INTO chapter2.items (user_id, title, content) VALUES (1, "a", "foo");
INSERT INTO chapter2.items (user_id, title, content) VALUES (2, "b", "bar");
INSERT INTO chapter2.items (user_id, title, content) VALUES (1, "c", "baz");

-- INNER JOIN: itemsが存在するユーザーとそのアイテムを抽出する (AND結合)
SELECT users.id, users.name, items.title, items.content FROM users INNER JOIN items ON users.id = items.user_id

-- OUTER JOIN: 全ユーザーとそのアイテムを抽出する (OR結合)
SELECT * FROM users LEFT OUTER JOIN items ON users.id = items.user_id;
```

テーブル・データベースの削除

```sql
-- テーブルの中身をすべて削除する
TRUNCATE TABLE chapter2.items;

-- テーブルを削除する
DROP TABLE items;
DROP TABLE users;

-- データベースを削除する
DROP DATABASE chapter2

-- MySQLからログアウト
exit;
```

# ■ Pythonからデータベースを触ってみる (SQLAlchemy)

[SQLAlchemy](https://www.sqlalchemy.org/)

## データベースの作成

```bash
# 開発用shellを起動
./bin/run.sh chapter2 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter2"
```

## JupyterLab起動

```bash
./bin/run.sh chapter2 --mode jupyter
```

`tutorial/chapter2/sample/sqlalchemy_tutorial.ipynb` の実装を参考に、SQLAlchemyを利用してPythonからデータベースを操作してみましょう。