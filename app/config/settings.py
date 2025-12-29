from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Database
    ORACLE_HOST: str = "localhost"
    ORACLE_PORT: int = 1521
    SERVICE_NAME: str = "FREEPDB1"

    # Service account
    ORACLE_SERVICE_USERNAME: str = "hospital_admin"
    ORACLE_SERVICE_PASSWORD: str = "tmp"

    # Pool config
    DB_POOL_ALIAS: str = "hospital_pool"
    DB_POOL_MIN: int = 1
    DB_POOL_MAX: int = 25
    DB_POOL_INCREMENT: int = 1
    DB_POOL_HOMOGENEOUS: bool = False # Heterogeneous pool required for proxy auth

    # JWT Auth
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 5

settings = Settings()
