"""Configuration management for Mind v5.

Configuration is loaded from environment variables with MIND_ prefix.
Tier auto-detection:
- MIND_TIER=standard: PostgreSQL only, embedded PG for local dev
- MIND_TIER=enterprise: Full Docker stack (NATS, Qdrant, FalkorDB, Temporal)
- If not set: Auto-detect based on configured services
"""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MIND_",
        extra="ignore",
    )

    # Tier configuration
    tier: Literal["standard", "enterprise", "auto"] = "auto"

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "mind"
    postgres_password: SecretStr = SecretStr("mind")
    postgres_db: str = "mind"

    @property
    def postgres_url(self) -> str:
        """Build PostgreSQL connection URL."""
        password = self.postgres_password.get_secret_value()
        return f"postgresql+asyncpg://{self.postgres_user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def postgres_url_sync(self) -> str:
        """Build synchronous PostgreSQL connection URL (for migrations)."""
        password = self.postgres_password.get_secret_value()
        return f"postgresql://{self.postgres_user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # NATS
    nats_url: str = "nats://localhost:4222"
    nats_user: str | None = None
    nats_password: SecretStr | None = None

    # Vector store configuration
    # Options: "pgvector" (default, built into PostgreSQL) or "qdrant" (dedicated vector DB)
    vector_backend: Literal["pgvector", "qdrant"] = "pgvector"

    # Qdrant (used when vector_backend="qdrant")
    qdrant_url: str | None = None
    qdrant_api_key: SecretStr | None = None

    # FalkorDB (graph database for causal inference)
    falkordb_host: str | None = None
    falkordb_port: int = 6379
    falkordb_password: SecretStr | None = None

    # Embedding
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    openai_api_key: SecretStr | None = None

    # Temporal
    temporal_host: str = "localhost"
    temporal_port: int = 7233
    temporal_namespace: str = "default"

    # Security
    jwt_secret: SecretStr | None = None
    encryption_key: SecretStr | None = None  # Fernet key for field-level encryption
    require_auth: bool = False  # Require JWT auth (auto-enabled in production)

    # Observability
    otel_exporter_otlp_endpoint: str | None = None
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "console"

    # Embedded PostgreSQL (Standard tier)
    embedded_pg_port: int = 5433
    embedded_pg_data_dir: str | None = None  # Defaults to ~/.mind/data/postgres

    # Database URL override (for cloud PostgreSQL like Supabase, Neon, etc.)
    database_url: str | None = None

    def get_effective_tier(self) -> Literal["standard", "enterprise"]:
        """Determine the effective tier based on config and available services.

        Priority:
        1. Explicit MIND_TIER setting (standard/enterprise)
        2. Auto-detect: If FalkorDB or Temporal host is configured, use Enterprise
        3. Default: Standard

        Returns:
            The effective tier to use
        """
        if self.tier == "standard":
            return "standard"
        elif self.tier == "enterprise":
            return "enterprise"

        # Auto-detect based on configured services
        # Enterprise requires dedicated infrastructure
        if self.falkordb_host or self.temporal_host != "localhost":
            return "enterprise"

        # Qdrant configured explicitly means Enterprise
        if self.qdrant_url:
            return "enterprise"

        # Default to Standard (PostgreSQL only)
        return "standard"

    def is_standard_tier(self) -> bool:
        """Check if running in Standard tier."""
        return self.get_effective_tier() == "standard"

    def is_enterprise_tier(self) -> bool:
        """Check if running in Enterprise tier."""
        return self.get_effective_tier() == "enterprise"

    def get_database_url(self) -> str | None:
        """Get the database URL to use.

        Returns:
            Database URL if configured, None for embedded PostgreSQL
        """
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
