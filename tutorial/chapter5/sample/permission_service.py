import enum
from typing import Dict, Set, List, Callable
from model import User, RoleType
from functools import wraps

# 権限の定義
class PermissionType(enum.Enum):
    USER_CREATE = "USER_CREATE"
    USER_READ   = "USER_READ"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    ITEM_CREATE = "ITEM_CREATE"
    ITEM_READ   = "ITEM_READ"
    ITEM_UPDATE = "ITEM_UPDATE"
    ITEM_DELETE = "ITEM_DELETE"


# 権限を扱うユーティリティクラス
class PermissionService:
    # どのロールが何の権限を持っているのかをクラス変数で定義
    __role_definition: Dict[RoleType, Set[PermissionType]] = {
        RoleType.SYSTEM_ADMIN: set([  # SYSTEM_ADMIN が保有する権限
            PermissionType.USER_CREATE,
            PermissionType.USER_READ,
            PermissionType.USER_UPDATE,
            PermissionType.USER_DELETE,
            PermissionType.ITEM_CREATE,
            PermissionType.ITEM_READ,
            PermissionType.ITEM_UPDATE,
            PermissionType.ITEM_DELETE,
        ]),
        RoleType.LOCATION_ADMIN: set([  # LOCATION_ADMIN が保有する権限
            PermissionType.USER_READ,
            PermissionType.USER_UPDATE,
            PermissionType.ITEM_CREATE,
            PermissionType.ITEM_READ,
            PermissionType.ITEM_UPDATE,
            PermissionType.ITEM_DELETE,
        ]),
        RoleType.LOCATION_OPERATOR: set([  # LOCATION_OPERATOR が保有する権限
            PermissionType.ITEM_CREATE,
            PermissionType.ITEM_READ,
            PermissionType.ITEM_UPDATE,
            PermissionType.ITEM_DELETE,
        ])
    }

    @classmethod
    def has_permission(cls, user: User, permissions: List[PermissionType]) -> bool:
        """引数で受け取った権限を有しているかを確認するメソッド"""
        required_permissions = set(permissions)
        user_permissions = cls.get_permissions(user)
        return len(required_permissions) == len(required_permissions & user_permissions)

    @classmethod
    def get_permissions(cls, user: User) -> Set[PermissionType]:
        """ユーザーが保持している権限を取得するメソッド"""
        ret = set()
        for role in user.roles:
            ret = ret | cls.__role_definition.get(role.name, set())
        return ret