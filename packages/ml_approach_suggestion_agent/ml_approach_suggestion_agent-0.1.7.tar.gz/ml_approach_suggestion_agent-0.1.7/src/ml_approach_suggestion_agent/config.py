from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict




class MethodologyConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    methodology_ai_provider: str = Field(default="openai", description="AI provider to use")
    methodology_ai_model: str = Field(default="gpt-5-mini", description="AI model to use")
    methodology_temperature: float = Field(default=0.3, ge=0.0, le=0.5, description="AI model temperature")
    methodology_max_tokens: int = Field(default=4000, ge=100, le=8000, description="Maximum tokens for AI response")


