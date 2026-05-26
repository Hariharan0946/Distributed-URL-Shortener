from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite:///./test_shortener.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_and_resolve_short_url() -> None:
    response = client.post("/api/v1/shorten", json={"url": "https://example.com/long/path"})
    assert response.status_code == 201
    payload = response.json()
    short_code = payload["short_code"]

    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/long/path"


def test_custom_alias_conflict() -> None:
    first = client.post(
        "/api/v1/shorten",
        json={"url": "https://example.com/a", "custom_alias": "resume-demo"},
    )
    second = client.post(
        "/api/v1/shorten",
        json={"url": "https://example.com/b", "custom_alias": "resume-demo"},
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_stats_reflect_clicks() -> None:
    create_response = client.post("/api/v1/shorten", json={"url": "https://example.com/stats"})
    short_code = create_response.json()["short_code"]

    client.get(f"/{short_code}", follow_redirects=False)
    client.get(f"/{short_code}", follow_redirects=False)

    stats_response = client.get(f"/api/v1/stats/{short_code}")
    assert stats_response.status_code == 200
    assert stats_response.json()["click_count"] == 2

