from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class Parameters(BaseModel):
    """Water quality and operational parameters"""
    turbidity: float = Field(..., ge=0.0, le=2.0, description="Turbidity in NTU")
    ph: float = Field(..., ge=4.0, le=10.0, description="pH value")
    temperature: float = Field(..., ge=15.0, le=35.0, description="Temperature in °C")
    flow_rate: float = Field(..., ge=10.0, le=50.0, description="Flow rate in GPM")
    inlet_pressure: float = Field(..., ge=20.0, le=80.0, description="Inlet pressure in PSIG")

class BackwashPoint(BaseModel):
    """Backwash point information"""
    time_step: int = Field(..., description="Time step when backwash occurs")
    pressure: float = Field(..., description="Pressure at backwash point")
    intensity: float = Field(..., description="Backwash intensity in W")
    duration: int = Field(..., description="Backwash duration in seconds")
    reason: str = Field(..., description="Reason for backwash")

class PredictionData(BaseModel):
    """Prediction result data"""
    pressure_data: List[float] = Field(..., description="Pressure values over time")
    backwash_points: List[BackwashPoint] = Field(default=[], description="Backwash points")
    fouling_rate: float = Field(..., description="Fouling rate")
    efficiency: float = Field(..., description="System efficiency")
    recommendations: List[str] = Field(default=[], description="System recommendations")
    confidence_score: Optional[float] = Field(None, description="Prediction confidence score")

class PredictionRequest(BaseModel):
    """Prediction request model"""
    parameters: Parameters = Field(..., description="Water quality parameters")
    fouling_status: str = Field(..., description="Fouling status")
    time_steps: int = Field(default=20, ge=1, le=50, description="Number of time steps")
    pressure_threshold: float = Field(default=7.0, description="Pressure threshold for backwash")

class PredictionResponse(BaseModel):
    """Prediction response model"""
    success: bool = Field(..., description="Request success status")
    prediction_data: PredictionData = Field(..., description="Prediction results")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")

class CurveData(BaseModel):
    """Curve data for advanced predictions"""
    turbidity_curve: Optional[List[float]] = Field(None, description="Turbidity curve over time")
    ph_curve: Optional[List[float]] = Field(None, description="pH curve over time")
    temperature_curve: Optional[List[float]] = Field(None, description="Temperature curve over time")

class AdvancedPredictionRequest(BaseModel):
    """Advanced prediction request with curve data"""
    parameters: Parameters = Field(..., description="Base water quality parameters")
    curve_data: Optional[CurveData] = Field(None, description="Curve data for time-varying parameters")
    fouling_status: str = Field(default="clean", description="Fouling status")
    time_steps: int = Field(default=20, ge=1, le=50, description="Number of time steps")

class HistoryRecord(BaseModel):
    """Historical prediction record"""
    id: str = Field(..., description="Record ID")
    timestamp: datetime = Field(..., description="Prediction timestamp")
    parameters: Parameters = Field(..., description="Input parameters")
    prediction_accuracy: float = Field(..., description="Prediction accuracy")
    backwash_points: List[BackwashPoint] = Field(default=[], description="Predicted backwash points")

class HistoryResponse(BaseModel):
    """History response model"""
    success: bool = Field(..., description="Request success status")
    history: List[HistoryRecord] = Field(..., description="Historical records")
    total_count: int = Field(..., description="Total number of records") 