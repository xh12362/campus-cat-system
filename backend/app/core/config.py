from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_UPLOAD_DIR = Path("/workspace/uploads/original")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Campus Cat Backend"
    debug: bool = False
    mysql_host: str = Field(default="mysql", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_database: str = Field(default="campus_cat", alias="MYSQL_DATABASE")
    mysql_user: str = Field(default="cat_user", alias="MYSQL_USER")
    mysql_password: str = Field(default="cat_password", alias="MYSQL_PASSWORD")
    upload_dir: Path = Field(default=DEFAULT_UPLOAD_DIR, alias="UPLOAD_DIR")
    cors_origins: list[str] = ["*"]

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )


settings = Settings()
