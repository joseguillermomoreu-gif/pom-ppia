"""Configuración centralizada de la aplicación."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración centralizada usando Pydantic Settings.

    Lee variables de entorno desde .env
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")

    # Anthropic (opcional, futuro)
    anthropic_api_key: Optional[str] = Field(
        None, description="Anthropic API key (optional)"
    )

    # LLM Provider
    llm_provider: str = Field(default="openai", description="LLM provider to use")
    default_model: str = Field(
        default="gpt-4o-mini", description="Default model to use"
    )

    # LLM Parameters
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Temperature for generation"
    )
    max_tokens: int = Field(
        default=4000, ge=1, le=128000, description="Max tokens in response"
    )

    # Paths
    output_dir: Path = Field(default=Path("./output"), description="Output directory")
    config_file: Path = Field(
        default=Path("./config/llm-providers.yaml"),
        description="LLM providers config",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    def __init__(self, **kwargs):
        """Initialize settings and create output dir if needed."""
        super().__init__(**kwargs)
        self.output_dir.mkdir(parents=True, exist_ok=True)


# Singleton instance
settings = Settings()
