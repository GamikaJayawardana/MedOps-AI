from pydantic import SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: SecretStr = SecretStr("")
    pinecone_api_key: SecretStr = SecretStr("")
    database_url: str = ""     

    class Config:
        env_file = ".env"


settings = Settings()