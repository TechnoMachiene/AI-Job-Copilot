from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str
    min_match_score: int = 75
    
    # Candidate Baseline Info
    candidate_name: str
    candidate_email: str
    candidate_phone: str
    
    # Email Adapter Config
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Global singleton for settings
settings = Settings()