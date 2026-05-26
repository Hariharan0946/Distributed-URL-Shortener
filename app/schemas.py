from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    custom_alias: str | None = Field(default=None, min_length=4, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    expires_at: datetime | None


class URLStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str
    click_count: int
    created_by_node: str
    created_at: datetime
    expires_at: datetime | None
    last_accessed_at: datetime | None


class HealthResponse(BaseModel):
    status: str
    node_id: str
    cache_enabled: bool

