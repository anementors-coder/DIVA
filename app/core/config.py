from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os 


BASEDIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE_PATH = os.path.join(BASEDIR, '.env')
# print(f"Base directory for env file: {BASEDIR}")
# print(f"Full path to env file: {ENV_FILE_PATH}")

class Settings(BaseSettings):
    # These are the variables Pydantic will read from the .env file
    APP_NAME: str = "AI Mentor API"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    PASSPORT_PUBLIC_KEY: str
    EXPECTED_AUD: str = "1"
    CLOCK_SKEW_LEEWAY: int = 10
    # NEXTJS_SECRET_KEY: str
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    DATABASE_PORT: int
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET_NAME: str = os.getenv("AWS_S3_BUCKET_NAME", "")
    
    # Optional: Use IAM role instead of access keys (recommended for production)
    AWS_USE_IAM_ROLE: bool = os.getenv("AWS_USE_IAM_ROLE", "false").lower() == "true"
    
    # Optional: Custom domain for S3 (CloudFront)
    AWS_S3_CUSTOM_DOMAIN: str = os.getenv("AWS_S3_CUSTOM_DOMAIN", "")
    
    # File upload settings
    MAX_RESUME_FILE_SIZE: int = int(os.getenv("MAX_RESUME_FILE_SIZE", 5 * 1024 * 1024))  # 5MB
    

    
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
# if Path(settings.PASSPORT_PUBLIC_KEY).exists():
#     with open(settings.PASSPORT_PUBLIC_KEY, "r", encoding="utf-8") as f:
#         settings.PASSPORT_PUBLIC_KEY = f.read()