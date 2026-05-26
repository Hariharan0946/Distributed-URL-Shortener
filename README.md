# Distributed URL Shortener

A distributed URL shortener built with FastAPI, PostgreSQL, Redis, and Nginx. The system converts long URLs into compact short links, distributes traffic across multiple API nodes, and uses shared storage plus caching for consistency and performance.

## Architecture

`Nginx -> FastAPI nodes -> PostgreSQL`

`FastAPI nodes <-> Redis`

- `api1` and `api2` simulate horizontally scaled application nodes.
- PostgreSQL stores URL mappings, expiration data, and click analytics.
- Redis caches hot URL lookups to reduce repeated database reads.
- Each API node uses a distinct `WORKER_ID` for Snowflake-style distributed ID generation.

## Features

- Generate short URLs for long links
- Support optional custom aliases
- Configure expiration for shortened links
- Redirect short links to original URLs
- Track click counts and access metadata
- Expose per-link analytics through a stats endpoint
- Run multiple API nodes behind an Nginx load balancer

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- Nginx
- Docker Compose
- Pytest

## API Endpoints

### `POST /api/v1/shorten`

Creates a shortened URL.

Request:

```json
{
  "url": "https://example.com/some/very/long/path",
  "custom_alias": "demo-link",
  "expires_in_days": 30
}
```

Response:

```json
{
  "short_code": "abc123",
  "short_url": "http://localhost:8080/abc123",
  "original_url": "https://example.com/some/very/long/path",
  "expires_at": "2026-06-26T12:00:00"
}
```

### `GET /{short_code}`

Redirects to the original URL and increments the click count.

### `GET /api/v1/stats/{short_code}`

Returns stored metadata and analytics for a short code.

### `GET /health`

Returns service health information and the current node ID.

## Local Development

### Run with Python

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
copy .env.example .env
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, and the interactive docs will be available at `http://localhost:8000/docs`.

### Run with Docker Compose

```bash
docker compose up --build
```

The load-balanced API will be available at `http://localhost:8080`, and the interactive docs will be available at `http://localhost:8080/docs`.

## Environment Variables

- `BASE_URL`: Base URL used when constructing shortened links
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `WORKER_ID`: Unique numeric node identifier for distributed ID generation
- `NODE_ID`: Human-readable node name exposed by the health endpoint

## Testing

```bash
pytest
```
