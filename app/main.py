"""
FastAPI REST API for Flight Delay Prediction service.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.feature_engineering import hash_airport_code

app = FastAPI(
    title="Flight Delay Prediction API",
    description="MLOps Homework 2 - CI/CD Pipeline Demo",
    version="1.0.0"
)


class PredictionRequest(BaseModel):
    """Request model for /predict endpoint."""
    departure_airport: str = Field(..., description="IATA airport code (e.g., 'JFK')")


class PredictionResponse(BaseModel):
    """Response model for /predict endpoint."""
    bucket: int = Field(..., description="Hash bucket index (0 to 99)")


class HealthResponse(BaseModel):
    """Response model for /health endpoint."""
    status: str = Field(default="ok", description="Service status")


@app.get("/health", response_model=HealthResponse, status_code=200)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with status="ok"
    """
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse, status_code=200)
async def predict(request: PredictionRequest):
    """
    Predict hash bucket for departure airport code.
    
    Args:
        request: PredictionRequest with departure_airport field
    
    Returns:
        PredictionResponse with bucket index
    
    Raises:
        HTTPException: If airport code is invalid
    """
    try:
        bucket = hash_airport_code(request.departure_airport, num_buckets=100)
        return {"bucket": bucket}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

