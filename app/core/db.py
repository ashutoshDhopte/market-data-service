import os

import structlog
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = structlog.get_logger(__name__)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set", exc_info=True)
    raise ValueError("DATABASE_URL environment variable not set")

# The engine is the entry point to the database.
engine = create_engine(DATABASE_URL)

# A SessionLocal class is a factory for new Session objects.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base will be used by our ORM models to inherit from.
Base = declarative_base()


# Dependency for FastAPI: This function will be called for each request
# that depends on a database session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
