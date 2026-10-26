"""
Configuration management for Bible MCP Server

Combines mcp-service-kit configuration classes with Bible-specific settings.
Each section reads its own environment variables when instantiated.
"""

from typing import Annotated, List

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from mcp_service_kit import BaseServerConfig


class BibleAPIConfig(BaseSettings):
    """
    Configuration for Bible API

    Environment variables: BIBLE_API_URL, BIBLE_DEFAULT_VERSION,
    BIBLE_SUPPORTED_VERSIONS (comma-separated), BIBLE_TIMEOUT
    """
    model_config = SettingsConfigDict(env_prefix="BIBLE_", extra="ignore")

    api_url: str = Field(
        default="https://www.biblegateway.com/passage/",
        description="Bible Gateway base URL"
    )
    default_version: str = Field(
        default="ESV",
        description="Default Bible version"
    )
    supported_versions: Annotated[List[str], NoDecode] = Field(
        default=["ESV", "NIV", "KJV", "NASB", "NKJV", "NLT", "AMP", "MSG"],
        description="List of supported Bible versions"
    )
    timeout: float = Field(
        default=30.0,
        gt=0,
        description="HTTP request timeout in seconds"
    )

    @field_validator("supported_versions", mode="before")
    @classmethod
    def _split_versions(cls, value: object) -> object:
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


class AppConfig(BaseModel):
    """
    Complete application configuration

    Aggregates all configuration sections into a single object. The server
    section is passed to the server; the rest go to the service.
    """
    server: BaseServerConfig = Field(default_factory=BaseServerConfig)
    bible_api: BibleAPIConfig = Field(default_factory=BibleAPIConfig)
