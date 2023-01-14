from pydantic import BaseSettings

class Environment(BaseSettings):
    """環境変数を定義する構造体。
    pydanticを利用した環境変数の読み込み: https://fastapi.tiangolo.com/advanced/settings/#environment-variables
    """
    db_user: str
    db_password: set
    db_port: str
    db_host: str
    db_name: str = "chapter3"