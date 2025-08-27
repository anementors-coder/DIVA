from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os 

BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
ENV_FILE_PATH = os.path.join(BASEDIR, '.env')


class Settings(BaseSettings):
    # These are the variables Pydantic will read from the .env file
    APP_NAME: str = "AI Mentor API"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    PASSPORT_PUBLIC_KEY: str
    EXPECTED_AUD: str = "1"
    CLOCK_SKEW_LEEWAY: int = 10

    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    DATABASE_PORT: int
    
    @property
    def DATABASE_URL(self) -> str:
        url = f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}" \
            f"@{self.POSTGRES_SERVER}:{self.DATABASE_PORT}/{self.POSTGRES_DB}"
        return url


    # This tells Pydantic where to load the .env file from, using the absolute path
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH, extra='ignore')
    # print(f"model config: {model_config}")
    # print(f"env file path: {ENV_FILE_PATH}")

settings = Settings()
# If PASSPORT_PUBLIC_KEY is actually a file path, load the file
if Path(settings.PASSPORT_PUBLIC_KEY).exists():
    with open(settings.PASSPORT_PUBLIC_KEY, "r", encoding="utf-8") as f:
        settings.PASSPORT_PUBLIC_KEY = f.read()