from pydantic import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = "database"
    secret_key_jwt: str = "secret_key"
    algorithm: str = "algorithm"

    mail_username: str = "user"
    mail_password: str = "password"
    mail_from: str = "mail"
    mail_port: int = 987654
    mail_server: str = "server"

    redis_host: str = "localhost"
    redis: int = 123456

    cloudinary_name: str = "name"
    cloudinary_api_key: int = 654321
    cloudinary_secret: str = "secret"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
