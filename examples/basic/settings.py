from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Settings for the example.
    """

    solarnetwork_host: str
    solarnetwork_token: str
    solarnetwork_secret: str

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env")


settings = Settings()
