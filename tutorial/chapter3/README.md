[Chapter3] Alembicを利用したマイグレーションを実装してみよう
--
[top](../../README.md)

# Note

このドキュメントでは `bin` 配下のコマンド以外は `tutorial/chapter3/src` をルートディレクトリとして解説します。

chapter2ではPythonからSQLAlchemyを利用してデータベースを操作する方法を学びました。 chapter3では、Pythonのモデル定義と実際のDBを同期させる方法を学びましょう。  

当然ですが、テーブル定義はアプリの開発・運用を行う過程で変更されます。  
例えばusersテーブルにカラムが追加されたとします。Python側で変更されたモデルに実際のDBはどのように同期させるべきでしょうか。  
手動で更新する方法はなるべく避けたいですね。一般的にPythonではモデルの定義とDBを同期させるためのライブラリとして[Alembic](https://alembic.sqlalchemy.org/en/latest/)を利用します。(このようなライブラリをDBマイグレーションライブラリと呼びます)  


ちなみに。。。 DBにログインして `ALTER TABLE ...` を手動で実行した場合、下記のような問題が発生します。

1. 単純テーブルの更新を忘れる  
一つのアプリでも、開発環境、ステージング環境、本番環境など、複数の環境があることが一般的です。  
どの環境にどこまで変更を適用したのかを正確に管理するのは容易ではありません。  

1. テーブル定義への変更履歴が残らない  
いつ、どのようにテーブル定義を変更したのかが、ソースコードに残りません。
デプロイ後にバージョンを切り戻したいと思っても、変更履歴がないため切り戻すためのコマンドがわかりません。


# ■ mysqlを起動しましょう

※ 起動していない場合のみ

```bash
./bin/mysql.sh
```

# ■ モデルの実装

まずは環境変数をPythonで扱うためのコードを書いていきます。  
FastApiは `pydantic` というライブラリを利用して型をある程度厳密に扱う方針のフレームワークです。  
環境変数もこの `pydantic` を利用して、オブジェクトとして扱います。こうすることで、利用する環境変数とその型をソースコードに明示することができます。

[pydanticを利用した環境変数の読み込み](https://fastapi.tiangolo.com/advanced/settings/#environment-variables)

```python
# -- env.py --

from pydantic_settings import BaseSettings

class Environment(BaseSettings):
    db_user: str
    db_password: str
    db_port: str
    db_host: str
    db_name: str = "chapter3"
```

次にDBのセッションを管理する、セッションファクトリーを定義します。

```python
# -- session.py --
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from env import Environment

env = Environment()
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{env.db_user}:{env.db_password}@{env.db_host}:{env.db_port}/{env.db_name}?charset=utf8mb4"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush = True, bind=engine)

def get_session():
    """DBのセッションを生成する。
    1リクエスト1セッションの想定で、 レスポンスが返却される際に自動でcloseされる。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

chapter2と同様に、users, items, roles, user_rolesテーブルに相当するモデルを定義します。

```python
# -- model.py --

import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime, Enum
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMTEXT

# モデルのベースクラスを定義
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

    # リレーション (many to many)
    #   多対多のリレーション: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
    roles = relationship("Role", secondary="user_roles", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username},items={self.items}, roles={self.roles})>"


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

class UserRole(Base):
    """users と roles の中間テーブル"""
    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="unique_idx_userid_roleid"),  # user_idとrole_idを複合ユニークキーに設定する
        {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4','mysql_collate':'utf8mb4_bin'}
    )

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

class RoleType(str, enum.Enum):
    SYSTEM_ADMIN      = "SYSTEM_ADMIN"
    LOCATION_ADMIN    = "LOCATION_ADMIN"
    LOCATION_OPERATOR = "LOCATION_OPERATOR"

class Role(Base):
    """roles テーブルの定義
    """
    __tablename__ = "roles"
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4','mysql_collate':'utf8mb4_bin'}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(RoleType), unique=True, index=True, nullable=False)  # ロール名
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # リレーション (many to many)
    users = relationship("User", secondary="user_roles", back_populates="roles")

    def __repr__(self):
        return f"""<Roles(id={self.id}, name={self.name})>"""
```


# ■ alembicプロジェクトの作成

[alembicドキュメント](https://alembic.sqlalchemy.org/en/latest/)

```bash
# 開発用shellを起動
./bin/run.sh chapter3 --mode shell

# chapter3データベースを作成
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT -e "CREATE DATABASE IF NOT EXISTS chapter3"

# alembicプロジェクトを作成
mkdir alembic
alembic init alembic
```

alembicの設定ファイル `alembic.ini` の `sqlalchemy.url` にDBの接続情報を設定します。

```ini
# -- alembic.ini --

sqlalchemy.url = mysql+pymysql://root:root1234@10.29.10.100:63306/chapter3?charset=utf8mb4
```

先ほど定義したモデルクラスのメタデータをalembicに読み込ませます。  
`alembic/env.py` の `target_metadata` にベースクラスのメタデータを設定します。


```python
# -- alembic/env.py --

import model  # モデルクラスの読み込み
target_metadata = model.Base.metadata  # Baseクラスのメタデータ
```

alembicコマンドを利用して、マイグレーションファイルを自動生成してみましょう。

```bash
alembic revision --autogenerate -m "create initial table"
```

`alembic/versions/XXXXXXXXXXXXXXXXXXXX_create_initial_table.py` というマイグレーションファイルが生成されるので確認してみましょう
マイグレーションファイルには `update()` と `downgrade()` という関数が実装されており、 `upgrade()` はこのマイグレーションを適用するときに実行され、 `downgrade()` はバージョンを切り戻すときに実行されます。  
つまり、`upgrade()` の内容は現在のDBの状態とモデルとの差分がコマンドとなっており、 `downgrade()` の内容は `upgrade()` で作成したリソースを削除するコマンドとなっています。


```python
# -- alembic/versions/XXXXXXXXXXXXXXXXXXXX_create_initial_table.py --

"""create initial table

Revision ID: 8b66834003bf
Revises: 
Create Date: 2023-05-16 16:06:26.312281

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8b66834003bf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Enum('SYSTEM_ADMIN', 'LOCATION_ADMIN', 'LOCATION_OPERATOR', name='roletype'), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8mb4',
    mysql_collate='utf8mb4_bin',
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    # ... 略 ...


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_roles_id'), table_name='user_roles')
    op.drop_table('user_roles')
    op.drop_table('items')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_index(op.f('ix_roles_id'), table_name='roles')
    op.drop_table('roles')
    # ### end Alembic commands ###
```

マイグレーションファイルに処理を追加してみましょう。  
ロールは `SYSTEM_ADMIN` `LOCATION_ADMIN` `LOCATION_OPERATOR` の3つのみなので、マイグレーションファイル内で登録します。

```python
# -- alembic/versions/XXXXXXXXXXXXXXXXXXXX_create_initial_table.py --

# ... 略 ...
from datetime import datetime
from model import RoleType

def upgrade() -> None:
    # rolesテーブルのcreate_tableの戻り値を roles_table に代入
    roles_table = op.create_table('roles',
    # ... 略 ...
    now = datetime.now()
    op.bulk_insert(roles_table, [
        {
            'id': 1,
            "name": RoleType.SYSTEM_ADMIN.value,
            "created": now,
            "updated": now
        },
        {
            'id': 2,
            "name": RoleType.LOCATION_ADMIN.value,
            "created": now,
            "updated": now
        },
        {
            'id': 3,
            "name": RoleType.LOCATION_OPERATOR.value,
            "created": now,
            "updated": now
        },
    ])

```


マイグレーションを実行します

```bash
alembic upgrade head

# 履歴を確認してみましょう。 (先ほど作ったリビジョンがheadとなっているはずです。)
alembic history
# <base> -> 8b66834003bf (head), create initial table

# 現在適用されているリビジョンを確認してみましょう。 (先ほど作ったリビジョンが表示されるはずです。)
alembic current
# 8b66834003bf (head)


```

テーブルが生成されているか確認してみましょう

```bash
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT chapter3
```

```sql
-- テーブル一覧を表示
-- ※ alembic_versionテーブルはマイグレーションのバージョン管理をするためのテーブルです
SHOW TABLES;
+--------------------+
| Tables_in_chapter3 |
+--------------------+
| alembic_version    |
| items              |
| roles              |
| user_roles         |
| users              |
+--------------------+

-- テーブル定義を確認
DESC users;
+-----------------+--------------+------+-----+---------+----------------+
| Field           | Type         | Null | Key | Default | Extra          |
+-----------------+--------------+------+-----+---------+----------------+
| id              | int          | NO   | PRI | NULL    | auto_increment |
| username        | varchar(255) | NO   | UNI | NULL    |                |
| hashed_password | varchar(255) | NO   |     | NULL    |                |
| created         | datetime     | NO   |     | NULL    |                |
| updated         | datetime     | NO   |     | NULL    |                |
+-----------------+--------------+------+-----+---------+----------------+

DESC items;
+---------+--------------+------+-----+---------+----------------+
| Field   | Type         | Null | Key | Default | Extra          |
+---------+--------------+------+-----+---------+----------------+
| id      | int          | NO   | PRI | NULL    | auto_increment |
| user_id | int          | NO   | MUL | NULL    |                |
| title   | varchar(255) | NO   |     | NULL    |                |
| content | mediumtext   | YES  |     | NULL    |                |
| created | datetime     | NO   |     | NULL    |                |
| updated | datetime     | NO   |     | NULL    |                |
+---------+--------------+------+-----+---------+----------------+

DESC roles;
+---------+-----------------------------------------------------------+------+-----+---------+----------------+
| Field   | Type                                                      | Null | Key | Default | Extra          |
+---------+-----------------------------------------------------------+------+-----+---------+----------------+
| id      | int                                                       | NO   | PRI | NULL    | auto_increment |
| name    | enum('SYSTEM_ADMIN','LOCATION_ADMIN','LOCATION_OPERATOR') | NO   | UNI | NULL    |                |
| created | datetime                                                  | NO   |     | NULL    |                |
| updated | datetime                                                  | NO   |     | NULL    |                |
+---------+-----------------------------------------------------------+------+-----+---------+----------------+

DESC user_roles;
+---------+----------+------+-----+---------+----------------+
| Field   | Type     | Null | Key | Default | Extra          |
+---------+----------+------+-----+---------+----------------+
| id      | int      | NO   | PRI | NULL    | auto_increment |
| user_id | int      | NO   | MUL | NULL    |                |
| role_id | int      | NO   | MUL | NULL    |                |
| created | datetime | NO   |     | NULL    |                |
| updated | datetime | NO   |     | NULL    |                |
+---------+----------+------+-----+---------+----------------+

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

```

alembic/versions/ 配下にマイグレーションファイルができるので、確認してみましょう。usersテーブルにageカラムを追加するコマンドが記述されているはずです。

```python
# -- alembic/versions/XXXXXXXXXXXX_add_age_column_to_users_table.py --

# ... 略 ...


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'age')
    # ### end Alembic commands ###

```


マイグレーションを実行します。

```bash
# historyを確認すると先ほど追加したリビジョンがheadとなっています。
alembic history
# 8b66834003bf -> 906ffd5a0ff5 (head), add age column to users table
# <base> -> 8b66834003bf, create initial table

# 現在のリビジョンは "create initial table" のままです
alembic current
# 8b66834003bf

# マイグレーションを実行します
alembic upgrade head

# リビジョンが "add age column to users table" のリビジョンIDになっています。
alembic current
# 906ffd5a0ff5 (head)
```

テーブル定義が変更されているか確認してみましょう

```bash
MYSQL_PWD=$DB_PASSWORD mysql -u $DB_USER -h $DB_HOST -P $DB_PORT chapter3 -e "DESC users"
+-----------------+--------------+------+-----+---------+----------------+
| Field           | Type         | Null | Key | Default | Extra          |
+-----------------+--------------+------+-----+---------+----------------+
| id              | int          | NO   | PRI | NULL    | auto_increment |
| username        | varchar(255) | NO   | UNI | NULL    |                |
| hashed_password | varchar(255) | NO   |     | NULL    |                |
| created         | datetime     | NO   |     | NULL    |                |
| updated         | datetime     | NO   |     | NULL    |                |
| age             | int          | YES  |     | NULL    |                |
+-----------------+--------------+------+-----+---------+----------------+
```

ちなみに、リビジョンは柔軟に進めたり戻したりすることができます。いろいろ試してみましょう。

```bash
# リビジョンをひとつ前に戻すには
alembic downgrade -1

# リビジョンを一つ後ろに進めるには
alembic upgrade +1

# リビジョンを一番最初の状態に戻すには
alembic downgrade base

# リビジョンを最新の状態にするには
alembic upgrade head
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
