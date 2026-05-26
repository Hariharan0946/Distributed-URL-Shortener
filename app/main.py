from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.cache import CacheClient
from app.config import get_settings
from app.database import Base, engine, get_db
from app.schemas import HealthResponse, ShortenRequest, ShortenResponse, URLStatsResponse
from app.service import URLService

settings = get_settings()
cache = CacheClient(settings.redis_url, settings.cache_ttl_seconds)
service = URLService(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", node_id=service.node_id, cache_enabled=cache.enabled)


@app.post("/api/v1/shorten", response_model=ShortenResponse, status_code=201)
async def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)) -> ShortenResponse:
    short_url = service.create_short_url(db, payload)
    cache_payload = {
        "original_url": short_url.original_url,
        "expires_at": short_url.expires_at.isoformat() if short_url.expires_at else None,
    }
    await cache.set_url(short_url.short_code, cache_payload)
    return ShortenResponse(
        short_code=short_url.short_code,
        short_url=f"{settings.base_url.rstrip('/')}/{short_url.short_code}",
        original_url=short_url.original_url,
        expires_at=short_url.expires_at,
    )


@app.get("/{short_code}")
async def redirect_to_original(short_code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    cached = await cache.get_url(short_code)
    if cached:
        url = service.get_active_url(db, short_code)
    else:
        url = service.get_active_url(db, short_code)
        await cache.set_url(
            short_code,
            {
                "original_url": url.original_url,
                "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            },
        )

    service.register_click(db, url)
    return RedirectResponse(url=url.original_url, status_code=307)


@app.get("/api/v1/stats/{short_code}", response_model=URLStatsResponse)
def get_stats(short_code: str, db: Session = Depends(get_db)) -> URLStatsResponse:
    url = service.get_active_url(db, short_code)
    return URLStatsResponse.model_validate(url)

