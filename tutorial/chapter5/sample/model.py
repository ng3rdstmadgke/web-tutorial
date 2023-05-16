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
    age = Column(Integer, nullable=True)
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