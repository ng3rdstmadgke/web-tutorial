# ■ データベースの作成
```bash
# 開発用shellを起動
./bin/run.sh chapter3 --mode shell

# MySQLにログイン
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT
```

```sql
-- データベースの作成
CREATE DATABASE IF NOT EXISTS chapter3;

-- MySQLからログアウト
exit;
```

# ■ モデルの実装

# ■ alembicプロジェクトの作成

[alembicドキュメント](https://alembic.sqlalchemy.org/en/latest/)

```bash
# 開発用shellを起動
./bin/run.sh chapter3 --mode shell

# alembicプロジェクトを作成
mkdir alembic
alembic init alembic
```

alembicの設定ファイル `alembic.ini` の `sqlalchemy.url` にDBの接続情報を設定します。

```bash
vim alembic.ini
```

```ini
# -- alembic.ini --

sqlalchemy.url = mysql+pymysql://root:root1234@127.0.0.1:63306/chapter3?charset=utf8mb4
```

先ほど定義したモデルクラスのメタデータをalembicに読み込ませます。  
`alembic/env.py` の `target_metadata` にベースクラスのメタデータを設定します。


```bash
vim alembic/env.py
```

```python
# -- alembic/env.py --

from db import model  # モデルクラスの読み込み
target_metadata = model.Base.metadata  # Baseクラスのメタデータ
```

alembicコマンドを利用して、マイグレーションファイルを自動生成してみましょう。

```bash
alembic revision --autogenerate -m "create initial table"

# alembic/versions/ 配下にマイグレーションファイルができるので、確認してみましょう
vim alembic/versions/de6391e46756_create_initial_table.py
```

マイグレーションを実行します

```bash
alembic upgrade head
```

テーブルが生成されているか確認してみましょう

```bash
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT chapter3
```

```sql
-- テーブル一覧を表示
-- ※ alembic_versionテーブルはマイグレーションのバージョン管理をするためのテーブルです
SHOW TABLES;

-- テーブル定義を確認
DESC users;
DESC items;

-- ログアウト
exit;
```

# ■ モデルの変更を適用する

alembicはモデルの変更を検知して、現状との差分のマイグレーションファイルを自動生成できます。  
Userモデルに `age` カラムを追加して試してみましょう。

```bash
vim db/model.py
```

```python
# -- db/mode.py --

class User(Base):
   # ... 略 ...
    age = Column(Integer, nullable=True)
   # ... 略 ...
```

変更を保存したらマイグレーションファイルを自動生成します。

```bash
alembic revision --autogenerate -m "add age column to users table"

# alembic/versions/ 配下にマイグレーションファイルができるので、確認してみましょう
vim alembic/versions/6ada79cba7f4_add_age_column_to_users_table.py
```

マイグレーションを実行します。

```bash
alembic upgrade head
```

テーブルが生成されているか確認してみましょう

```bash
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT chapter3 -e "DESC users"
```

## ※ 【発展】自動検出される変更にはルールがあります

`alembic revision --autogenerate ...` で検出される変更は以下です。

- テーブルの追加、削除
- 列の追加、削除
- 列のNULL可能ステータスの変更
- インデックスの基本的な変更と明示的に名前が付けられたユニーク製薬
- 外部キー制約の基本的な変更

逆に検出できない変更には以下のようなものがあります

- 列名の変更
- 匿名で名前が付けられた制約
- EnumのようなSQLAlchemyの機能で、バックエンドのDBに機能がないもの。

詳しくはこちら -> [autogenerate | Alembic](https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)

# ■ そのほかのalembicコマンドの操作

alembicコマンドには `upgrade head` 以外にもバージョンをコントロールするいくつかのコマンドがあります。試してみましょう。

```bash
# ひとつ前のバージョンにロールバック
alembic downgrade -1

# 一つ次のバージョンにアップグレード:w
alembic upgrade +1

# マイグレーション履歴の確認
alembic history -v

# 最新までアップグレード
alembic upgrade head

# 一番最初までロールバック
alembic downgrade base
```
