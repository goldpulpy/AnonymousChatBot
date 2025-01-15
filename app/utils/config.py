"""Config utils"""
from typing import Any
from pydantic import BaseSettings, validator
from functools import lru_cache
import json


class BaseConfig(BaseSettings):
    """Base config with shared settings"""
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class DB(BaseConfig):
    """Database settings"""
    host: str
    port: int
    name: str
    user: str
    password: str

    class Config:
        env_prefix = 'DB_'


class Redis(BaseConfig):
    """Redis settings"""
    host: str
    db: int

    class Config:
        env_prefix = 'REDIS_'


class Bot(BaseConfig):
    """Bot settings"""
    token: str
    timezone: str
    admins: list[int]
    moders: list[int]
    use_redis: bool

    class Config:
        env_prefix = 'BOT_'

    @validator("admins", "moders", pre=True)
    def parse_json_list(cls, value: Any) -> list[int]:
        """Parse JSON string to list of integers"""
        return json.loads(value) if isinstance(value, str) else value


class Payments(BaseConfig):
    """Payments settings"""
    api_id: int
    api_key: str
    project_id: int
    project_secret: str
    enabled: bool

    class Config:
        env_prefix = 'PAYMENTS_'


class Settings(BaseConfig):
    """Settings class"""
    bot: Bot = Bot()
    db: DB = DB()
    redis: Redis = Redis()
    payments: Payments = Payments()


@lru_cache
def load_config() -> Settings:
    """
    Loads .env file into Settings
    Returns cached Settings instance
    """
    return Settings()
