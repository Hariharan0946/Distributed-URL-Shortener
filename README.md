# Distributed URL Shortener

A resume-ready distributed systems project that turns long URLs into compact short links, routes traffic across multiple API nodes, and uses Redis caching plus a shared database for consistency.

## Why this project works well for an SDE resume

- Designed a distributed URL shortener using FastAPI, PostgreSQL, Redis, and Nginx load balancing.
- Implemented Snowflake-style unique ID generation and Base62 encoding to create collision-resistant short codes across nodes.
- Added shared persistence, cache-backed reads, redirect tracking, and click analytics endpoints.
- Containerized the system with Docker Compose and validated core flows with automated API tests.

## Architecture

`Nginx -> FastAPI nodes -> PostgreSQL`

`FastAPI nodes <-> Redis`

- `api1` and `api2` simulate horizontally scaled application nodes.
- PostgreSQL is the source of truth for URL mappings and analytics counters.
- Redis caches hot URL lookups to reduce repeated database reads.
- Each node gets a distinct `WORKER_ID`, which feeds a Snowflake-style ID generator.

## Features

- Create short URLs with generated codes
- Optional custom aliases
- Expiration windows for links
- Redirect endpoint
- Click counting and usage stats
- Health endpoint that exposes node identity
- Multi-node local deployment with load balancing

## API

### `POST /api/v1/shorten`

Request:

```json
{
  "url": "https://example.com/some/very/long/path",
  "custom_alias": "resume-demo",
  "expires_in_days": 30
}
```

### `GET /{short_code}`

Redirects to the original URL and increments click count.

### `GET /api/v1/stats/{short_code}`

Returns metadata and click analytics for a short code.

### `GET /health`

Returns service health plus the current node ID.

## Run locally

### Option 1: Python

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
copy .env.example .env
uvicorn app.main:app --reload
```

### Option 2: Docker Compose

```bash
docker compose up --build
```

Then open `http://localhost:8080/docs`.

## Test

```bash
pytest
```

## How to explain the distributed aspect in interviews

- Multiple stateless API nodes sit behind Nginx, so traffic can be spread horizontally.
- Redis caches frequent lookups, reducing latency and database pressure.
- PostgreSQL acts as the durable shared store so all nodes see the same mappings.
- Worker-specific Snowflake IDs avoid coordination-heavy primary key generation at the app layer.

## Strong resume bullets

- Built a distributed URL shortener with FastAPI, PostgreSQL, Redis, and Nginx, supporting horizontal scaling across multiple API nodes.
- Implemented Snowflake-inspired ID generation and Base62 encoding to create globally unique short links with low collision risk.
- Improved read efficiency using Redis caching and exposed analytics endpoints for click tracking and operational visibility.
- Containerized the platform with Docker Compose and added automated tests for URL creation, redirection, and stats accuracy.
