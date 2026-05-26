from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.id_generator import SnowflakeGenerator, encode_base62, resolve_node_id
from app.models import ShortURL
from app.schemas import ShortenRequest


class URLService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.generator = SnowflakeGenerator(settings.worker_id)
        self.node_id = resolve_node_id()

    def create_short_url(self, db: Session, payload: ShortenRequest) -> ShortURL:
        short_code = payload.custom_alias or encode_base62(self.generator.generate())
        existing = db.scalar(select(ShortURL).where(ShortURL.short_code == short_code))
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Custom alias already exists." if payload.custom_alias else "Short code collision occurred.",
            )

        expires_days = payload.expires_in_days or self.settings.default_expiration_days
        expires_at = self._utcnow() + timedelta(days=expires_days)

        short_url = ShortURL(
            short_code=short_code,
            original_url=str(payload.url),
            created_by_node=self.node_id,
            expires_at=expires_at,
        )
        db.add(short_url)
        db.commit()
        db.refresh(short_url)
        return short_url

    def get_active_url(self, db: Session, short_code: str) -> ShortURL:
        url = db.scalar(select(ShortURL).where(ShortURL.short_code == short_code))
        if not url:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found.")
        expires_at = self._normalize_datetime(url.expires_at)
        if expires_at and expires_at < self._utcnow():
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Short URL has expired.")
        return url

    def register_click(self, db: Session, url: ShortURL) -> ShortURL:
        url.click_count += 1
        url.last_accessed_at = self._utcnow()
        db.add(url)
        db.commit()
        db.refresh(url)
        return url

    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _normalize_datetime(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return value.astimezone(UTC).replace(tzinfo=None) if value.tzinfo else value
