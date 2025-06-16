from fastapi import FastAPI
from app.api import prices

app = FastAPI(
    title="Blockhouse Capital Market Data Service",
    description="A microservice for fetching, processing, and serving market data.",
    version="1.0.0"
)

app.include_router(prices.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Market Data API"}

