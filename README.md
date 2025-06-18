# Market Data Service

## Overview
A microservice for fetching, processing, and serving market data.
Built with FastAPI, PostgreSQL, Redis, Kafka, and Docker.

- **API**: FastAPI app for market data endpoints
- **Consumer**: Kafka consumer for moving average calculation
- **Database**: PostgreSQL for persistent storage
- **Cache**: Redis for API response caching
- **Message Broker**: Kafka for event-driven processing

---

## Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local dev)

### Quick Start
```bash
# Start all services
./start.sh
```
Or manually:
```bash
docker-compose up --build
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

---

## API Documentation
Once running, visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

**Example Endpoint:**
- `GET /prices/latest?symbol=AAPL&provider_name=yfinance`  
  Returns the latest price for a symbol.

---

## Architecture Decisions
- **FastAPI** for async API and OpenAPI docs
- **PostgreSQL** for structured data storage
- **Redis** for caching with `fastapi-cache2`
- **Kafka** for decoupled event processing
- **Docker Compose** for orchestration
- **SQLAlchemy** for ORM and DB access

---

## Local Development
- Code is mounted into containers for live reload (`volumes` in `docker-compose.yml`)
- Use `pytest` for tests:  
  ```bash
  pytest
  ```
- Lint with `flake8`:
  ```bash
  flake8 .
  ```

---

## Troubleshooting
- **Database connection errors**: Ensure `db` service is healthy and `DATABASE_URL` is correct.
- **Kafka/Redis not ready**: Use wait scripts or increase wait time in `start.sh`.
- **Consumer not processing events**: Check Kafka topic and broker connectivity.
- **API not available**: Check logs with `docker-compose logs api`.
