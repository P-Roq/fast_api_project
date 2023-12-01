from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

config_path = os.getenv("PROJECTS_CONFIG")

dotenv_path = f'{config_path}/fast_api_project_demo_config/.env'
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    # Database related.
    username: str = os.getenv("USER_NAME")
    key_db: str = os.getenv("SECRET_KEY")
    port: str = os.getenv("PORT")
    host: str = os.getenv("HOST")
    database: str = os.getenv("DATABASE")
    # Token related.
    key_token: str = os.getenv('AUTH_SECRET_KEY')
    algorithm: str = os.getenv('AUTH_ALGORITHM')
    expiration_time: int = os.getenv('AUTH_ACCESS_TOKEN_EXPIRE_MINUTES')

settings = Settings()

