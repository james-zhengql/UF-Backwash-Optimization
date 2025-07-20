from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import numpy as np
from datetime import datetime
import uuid

# Fix import paths
from backend.models.prediction_model import PredictionModel
from backend.models.database import get_db, PredictionRecord
from backend.schemas.prediction import PredictionRequest, PredictionResponse, BackwashPoint
from backend.utils.validators import validate_parameters

app = FastAPI(
    title="Intelligent UF Backwash API",
    description="API for predicting UF membrane pressure and backwash requirements",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize prediction model
prediction_model = PredictionModel()

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Intelligent UF Backwash API", "version": "1.0.0"}

@app.get("/api/model/info")
async def get_model_info():
    """Get model information and supported parameters"""
    return {
        "model_version": "1.0.0",
        "supported_parameters": {
            "turbidity": {"min": 0.0, "max": 2.0, "unit": "NTU"},
            "ph": {"min": 4.0, "max": 10.0, "unit": ""},
            "temperature": {"min": 15.0, "max": 35.0, "unit": "°C"},
            "flow_rate": {"min": 10.0, "max": 50.0, "unit": "GPM"},
            "inlet_pressure": {"min": 20.0, "max": 80.0, "unit": "PSIG"}
        },
        "fouling_statuses": ["clean", "mild", "moderate", "severe", "critical"],
        "pressure_threshold": 7.0,
        "max_time_steps": 50
    }

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_backwash(request: PredictionRequest):
    """Predict pressure drop and backwash requirements"""
    try:
        # Validate input parameters
        validation_result = validate_parameters(request.parameters.dict())
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        # Generate prediction
        prediction_result = prediction_model.predict(
            parameters=request.parameters.dict(),
            fouling_status=request.fouling_status,
            time_steps=request.time_steps,
            pressure_threshold=request.pressure_threshold
        )
        
        # Create response
        response = PredictionResponse(
            success=True,
            prediction_data=prediction_result,
            metadata={
                "model_version": "1.0.0",
                "prediction_timestamp": datetime.utcnow().isoformat(),
                "confidence_score": prediction_result.get("confidence_score", 0.9)
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict/advanced")
async def predict_advanced(request: Dict[str, Any]):
    """Advanced prediction with curve data"""
    try:
        # Extract curve data if provided
        curve_data = request.get("curve_data", {})
        
        # Generate prediction with curve data
        prediction_result = prediction_model.predict_with_curves(
            base_parameters=request["parameters"],
            curve_data=curve_data,
            fouling_status=request.get("fouling_status", "clean"),
            time_steps=request.get("time_steps", 20)
        )
        
        return {
            "success": True,
            "prediction_data": prediction_result,
            "metadata": {
                "model_version": "1.0.0",
                "prediction_timestamp": datetime.utcnow().isoformat(),
                "uses_curve_data": bool(curve_data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_prediction_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """Get prediction history"""
    try:
        # This would typically query the database
        # For now, return mock data
        return {
            "success": True,
            "history": [
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": "2024-01-15T10:30:00Z",
                    "parameters": {
                        "turbidity": 0.5,
                        "ph": 7.0,
                        "temperature": 25.0
                    },
                    "prediction_accuracy": 0.92
                }
            ],
            "total_count": 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_status": "ready"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 