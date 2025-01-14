"""Config utils"""
import json

from pydantic import BaseSettings, validator


class DB(BaseSettings):
    """Database settings"""
    host: str
    port: int
    name: str
    user: str
    password: str


class Redis(BaseSettings):
    """Redis settings"""
    host: str
    db: int


class Bot(BaseSettings):
    """Bot settings"""
    token: str
    timezone: str
    admins: list[int]
    moders: list[int]
    use_redis: bool

    @validator("admins", pre=True, always=True)
    def admin_ids(cls, string) -> list[int]:

        return json.loads(string)

    @validator("moders", pre=True, always=True)
    def moder_ids(cls, string) -> list[int]:

        return json.loads(string)


class Payments(BaseSettings):
    """Payments settings"""
    api_id: int
    api_key: str
    project_id: int
    project_secret: str

    enabled: bool


class Settings(BaseSettings):
    """Settings class"""
    bot: Bot
    db: DB
    redis: Redis
    payments: Payments

    class Config:
        """Config class"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


def load_config(env_file: str = ".env") -> Settings:
    """
    Loads .env file into BaseSettings

    :param str env_file: Env file, defaults to ".env"
    :return Settings: Settings object
    """

    settings = Settings(_env_file=env_file)
    return settings
