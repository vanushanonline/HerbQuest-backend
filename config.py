from pydantic_settings import BaseSettings # NEW



class Settings(BaseSettings):
    database_url: str = "mongodb+srv://HerbQuest:HQ123@herbquestcluster.i9o4ky3.mongodb.net/"
    database_name: str = "HerbQuestDB"

    class Config:
        env_file = ".env"

settings = Settings()
