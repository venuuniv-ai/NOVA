from decimal import Decimal
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    auth_mode: Literal["demo", "local", "oidc"] = "local"
    auth_key_file: str = ""
    auth_audience: str = "nova-api"
    oidc_issuer: str = ""
    oidc_jwks_file: str = ""
    oidc_jwks_url: str = ""
    database_url: str = "postgresql+psycopg://nova:nova_local_only@localhost:5432/nova"
    redis_url: str = "redis://localhost:6379/0"
    local_model_enabled: bool = False
    local_model_base_url: str = "http://host.docker.internal:11434/v1"
    local_model_name: str = ""
    local_model_api_key: SecretStr | None = None
    local_model_timeout_seconds: float = Field(default=8, ge=1, le=30)
    local_model_reasoning_capable: bool = False
    daily_ai_budget_usd: Decimal = Field(default=Decimal(0), ge=0, le=25)
    max_request_cost_usd: Decimal = Field(default=Decimal(0), ge=0, le=25)
    model_cache_ttl_seconds: int = Field(default=300, ge=1, le=3600)
    allow_personal_cloud: bool = False
    media_directory: str = "/tmp/nova-media"
    max_image_bytes: int = Field(default=2_000_000, ge=1024, le=5_000_000)
    max_normalized_image_bytes: int = Field(default=8_000_000, ge=1024, le=16_000_000)
    max_image_width: int = Field(default=2048, ge=64, le=4096)
    max_image_height: int = Field(default=2048, ge=64, le=4096)
    max_image_pixels: int = Field(default=4_000_000, ge=4096, le=8_000_000)
    vision_clip_enabled: bool = False
    vision_clip_model_path: str = ""
    vision_dino_enabled: bool = False
    vision_dino_model_path: str = ""
    vision_sam_enabled: bool = False
    vision_sam_model_path: str = ""
    memory_embeddings_enabled: bool = False
    memory_embedding_base_url: str = "http://localhost:11434/v1"
    memory_embedding_model: str = ""
    memory_embedding_dimension: int = Field(default=32, ge=1, le=2000)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
