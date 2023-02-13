# Note
このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter3/src` をルートディレクトリとして解説します。

# ■ mysqlを起動しましょう

※ 起動していない場合のみ

```bash
./bin/mysql.sh
```

# ■ データベースの作成
```bash
# 開発用shellを起動
./bin/run.sh chapter3 --mode shell

# データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter3"
```

# ■ モデルの実装

まずは環境変数をPythonで扱うためのコードを書いていきます。  
FastApiは `pydantic` というライブラリを利用して型をある程度厳密に扱う方針のフレームワークです。  
環境変数もこの `pydantic` を利用して、オブジェクトとして扱います。こうすることで、利用する環境変数とその型をソースコードに明示することができます。

[pydanticを利用した環境変数の読み込み](https://fastapi.tiangolo.com/advanced/settings/#environment-variables)

```python
# -- env.py --

from pydantic import BaseSettings

class Environment(BaseSettings):
    db_user: str
    db_password: str
    db_port: str
    db_host: str
    db_name: str = "chapter3"
```

次にDBのセッションを管理する、セッションファクトリーを定義します。

```python
# -- db/db.py --

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from env import Environment

# 環境変数を利用してDBのURLを生成
env = Environment()
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{env.db_user}:{env.db_password}@{env.db_host}:{env.db_port}/{env.db_name}?charset=utf8mb4"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush = True, bind=engine)

def get_session():
    """DBのセッションを生成する関数。
    1リクエスト1セッションの想定で、 レスポンスが返却される際に自動でcloseされる。
    いちいち with SessionLocal() as session: をやるのが面倒なのでこうする。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

chapter2と同様に、usersテーブルとitemsテーブルに相当するモデルを定義します。

```python
# -- db/model.py --

from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm.decl_api import declarative_base

Base = declarative_base()

class User(Base):
    """usersテーブル
    モデル定義: https://docs.sqlalchemy.org/en/14/tutorial/metadata.html#defining-table-metadata-with-the-orm
    """
    __tablename__ = "users"
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4','mysql_collate':'utf8mb4_bin'}
    
    id = Column(Integer, primary_key=True, index=True)
    # collation(照合順序): https://dev.mysql.com/doc/refman/8.0/ja/charset-mysql.html
    username = Column(String(255, collation="utf8mb4_bin"), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # itemsテーブルとの一対多のリレーション
    #   https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-many
    items = relationship(
        "Item",           # リレーションモデル名
        back_populates="users",      # リレーション先の変数名
        # カスケード: https://docs.sqlalchemy.org/en/14/orm/cascades.html
        #   "all, delete-orphan": userを削除したときに、関連する items を削除する
        #   "save-update": userを削除したときに、関連する items のuser_idをNullにする (default)
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username},items={self.items})>"


class Item(Base):
    """items テーブルの定義
    """
    __tablename__ = "items"
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4','mysql_collate':'utf8mb4_bin'}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(MEDIUMTEXT)
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    #  usersテーブルとのリレーション
    users = relationship("User", back_populates="items")

    def __repr__(self):
        return f"""<Items(id={self.id}, user_id={self.user_id}, title={self.title}, content={self.content})>"""
```


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

```ini
# -- alembic.ini --

sqlalchemy.url = mysql+pymysql://root:root1234@127.0.0.1:63306/chapter3?charset=utf8mb4
```

先ほど定義したモデルクラスのメタデータをalembicに読み込ませます。  
`alembic/env.py` の `target_metadata` にベースクラスのメタデータを設定します。


```python
# -- alembic/env.py --

from db import model  # モデルクラスの読み込み
target_metadata = model.Base.metadata  # Baseクラスのメタデータ
```

alembicコマンドを利用して、マイグレーションファイルを自動生成してみましょう。

```bash
alembic revision --autogenerate -m "create initial table"

# alembic/versions/ 配下にマイグレーションファイルができるので、確認してみましょう
less alembic/versions/de6391e46756_create_initial_table.py
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
less alembic/versions/6ada79cba7f4_add_age_column_to_users_table.py
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

# 一つ次のバージョンにアップグレード
alembic upgrade +1

# マイグレーション履歴の確認
alembic history -v

# 最新までアップグレード
alembic upgrade head

# 一番最初までロールバック
alembic downgrade base
```
