from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LineageConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )
    lineage_ai_provider: str = Field(
        default="cortex", description="AI provider to use"
    )
    lineage_model: str = Field(default="openai-gpt-4.1", description="AI model to use")
    lineage_temperature: float = Field(
        default=0.3, ge=0.0, le=2.0, description="AI model temperature"
    )
    lineage_max_tokens: int = Field(
        default=1000, ge=100, le=8000, description="Maximum tokens for AI response"
    )
    # llama3.1-70b

# openai-gpt-4.1