import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017/mediadb"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"
    hf_token: str = os.getenv("HF_TOKEN", "")
    upload_dir: str = "/tmp/uploads"

    model_config = {"env_file": ".env"}


settings = Settings()

os.makedirs(settings.upload_dir, exist_ok=True)
