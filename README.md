# Market Data Service

[Youtube demo](https://youtu.be/4fyELCZAGyc)

## Overview

A microservice for fetching, processing, and serving market data.
Built with FastAPI, PostgreSQL, Redis, Kafka, and Docker.

  - **API**: FastAPI app for market data endpoints, featuring structured logging and rate limiting.
  - **Consumer**: Resilient Kafka consumer for moving average calculation, built with a Dead Letter Queue (DLQ) pattern.
  - **Database**: PostgreSQL for persistent storage of raw data and processed metrics.
  - **Cache**: Redis for API response caching to improve performance.
  - **Message Broker**: Kafka for event-driven processing.

<img width="739" alt="System architeture" src="https://github.com/user-attachments/assets/359cf09d-1c13-4b41-9a67-d66f8f5d8cc4" />

<img width="716" alt="Flow diagram" src="https://github.com/user-attachments/assets/4d25a59e-cd75-4017-9cc7-70ff1d0e5b10" />

-----

## Setup

### Prerequisites

  - Docker & Docker Compose
  - Python 3.10+
  - An active virtual environment is highly recommended.

### Local Environment Setup

1.  **Clone the repository**
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up pre-commit hooks (Recommended):**
    ```bash
    pre-commit install
    ```

### Quick Start

To run the entire application stack for development:

```bash
# This script starts all Docker services and the local Python consumer.
./start.sh
```

Or manually:

```bash
# Start all background services (API, DB, Kafka, Redis)
docker-compose up --build -d

# In a separate terminal, start the Kafka consumer
python ma_consumer.py
```

### Environment Variables

Create a `.env` file in the project root. The application and Docker Compose file use the following variables:

  - `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:password@localhost:5432/mydatabase`)
  - `REDIS_URL`: Redis connection string (e.g., `redis://localhost:6379`)
  - `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address (e.g., `localhost:9092`)

-----

## API Documentation

Once running, visit **[http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)** for the interactive Swagger UI.

**Example Endpoint:**

  - `GET /prices/latest?symbol=AAPL&provider=yfinance`
    Returns the latest price for a symbol.

**Rate Limiting:**
The API is rate-limited to protect resources. Exceeding the limits will result in a `429 Too Many Requests` response.

  - `/prices/latest`: **5 requests per minute**.
  - `/prices/poll`: **10 requests per minute**.

-----

## Architecture Decisions

  - **FastAPI**: Chosen for its high performance, async capabilities, and automatic OpenAPI documentation generation.
  - **PostgreSQL**: A robust relational database for structured data storage and complex queries.
  - **Redis**: Used for high-speed, temporary API response caching to reduce load on downstream services. Implemented manually to coexist with rate limiting.
  - **Kafka**: Acts as a durable message broker to decouple the API (producer) from the data processing logic (consumer), enabling resilience and scalability.
  - **Kafka Consumer Pattern**: The `ma_consumer.py` script implements a **Dead Letter Queue (DLQ)** pattern to handle message processing failures, preventing the pipeline from getting stuck and allowing for offline analysis of problematic messages.
  - **Docker Compose**: Used for orchestrating the multi-container development environment, ensuring consistency and ease of setup.
  - **SQLAlchemy**: The preferred ORM for interacting with the PostgreSQL database in a Pythonic way.
  - **slowapi**: Integrated to provide robust rate-limiting capabilities.
  - **structlog**: Used to implement structured (JSON) logging, preparing the service for integration with centralized logging platforms like ELK or Splunk.

-----

## Local Development

### Code Quality & Formatting

This project uses **pre-commit hooks** to automatically enforce code quality. After running `pre-commit install`, `black`, `isort`, and `flake8` will run on every commit to automatically format your code and check for errors.

You can also run the tools manually:

  - **Auto-format code:**
    ```bash
    black .
    isort .
    ```
  - **Lint with `flake8`:**
    ```bash
    flake8 .
    ```

### Testing

The project includes unit and end-to-end tests.

  - **Run all tests:**
    ```bash
    pytest
    ```
  - **End-to-End Test (`tests/test_e2e.py`):** This test verifies the entire data pipeline. **It requires the full application stack to be running** (use `start.sh` or `docker-compose up` + the consumer).

-----

## CI/CD Pipeline

This repository uses **GitHub Actions** (`.github/workflows/ci.yml`) for continuous integration. The pipeline is triggered on every push and pull request to the `main` branch.

The pipeline performs the following steps:

1.  **Linting**: Checks the code for style issues with `flake8`.
2.  **Testing**: Starts all services using `docker-compose` and runs the `pytest` suite, including the end-to-end test.
3.  **Build Docker Image**: Verifies that the production `Dockerfile` is valid and can be built successfully.

You can test the CI workflow locally before pushing changes by using **[act](https://github.com/nektos/act)**.

```bash
# Run the default 'push' event workflow
act

# Run a specific job
act -j build-and-test
```

-----

## Troubleshooting

  - **Database connection errors**: Ensure the `db` service is healthy (`docker-compose ps`) and the `DATABASE_URL` in your `.env` file is correct for the local environment (points to `localhost`).
  - **Kafka/Redis not ready**: Use wait scripts or increase the `sleep` time in `start.sh`.
  - **Consumer not processing events**: Check Kafka topic and broker connectivity. Ensure the `KAFKA_BOOTSTRAP_SERVERS` in your `.env` file points to `localhost:9092`.
  - **API not available**: Check the API logs with `docker-compose logs api`.
  - **Pre-commit or Flake8 errors**: Use `black . && isort .` to automatically fix formatting. Manually address any remaining logical errors (like unused imports).

-----
