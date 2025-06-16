from fastapi import FastAPI

app = FastAPI(
    title="Blockhouse Capital Market Data Service",
    description="A microservice for fetching, processing, and serving market data.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Welcome to the Market Data API"}

