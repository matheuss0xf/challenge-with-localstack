from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='./.env', env_file_encoding='utf-8', case_sensitive=True
    )

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    AWS_ENDPOINT_URL: str

    AGE_GROUPS_TABLE: str
    ENROLLMENTS_TABLE: str
    QUEUE_NAME: str


settings = Settings()
