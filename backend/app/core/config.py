from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    """
    Centeral, typed application configuration.
    values are loaded from environment variables (or a .env file).
    Never hardcode config values elsewhere in the app - import `settings` instead.
    
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Enterprise RAG Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True


settings = Settings()