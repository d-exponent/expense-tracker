from pydantic import BaseSettings


class Settings(BaseSettings):
    # DATABASE SETTINGS
    db_username: str
    db_password: str
    db_name: str
    db_port: int
    db_host: str = "localhost"

    # # JWT SETTINGS
    jwt_expires_after: int
    jwt_algorithm: str
    jwt_secret: str

    # COOKIE
    cookie_key: str

    # EMAIL
    email_address: str
    email_password: str

    # TWILLO - SMS MESSAGING API CLIENT
    twillo_auth_token: str
    twillo_account_sid: str
    twillo_from_phone_number: str

    def get_sqlalchemy_connection_url(self):
        user = self.db_username
        password = self.db_password
        db = self.db_name
        return f"postgresql://{user}:{password}@localhost:5432/{db}"


settings = Settings(_env_file=".env")
