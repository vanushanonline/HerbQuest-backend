from pydantic_settings import BaseSettings # NEW

class Settings(BaseSettings):
    database_url: str = "mongodb+srv://HerbQuest:HQ@123@herbquestcluster.i9o4ky3.mongodb.net/?retryWrites=true&w=majority&appName=HerbQuestCluster"
    database_name: str = "herbquest"

    class Config:
        env_file = ".env"

settings = Settings()
