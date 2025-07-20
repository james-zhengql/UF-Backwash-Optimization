from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from typing import Optional

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./uf_backwash.db")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

class PredictionRecord(Base):
    """Database model for prediction records"""
    __tablename__ = "prediction_records"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Input parameters
    turbidity = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    flow_rate = Column(Float, nullable=False)
    inlet_pressure = Column(Float, nullable=False)
    
    # Prediction parameters
    fouling_status = Column(String, nullable=False)
    time_steps = Column(Integer, default=20)
    pressure_threshold = Column(Float, default=7.0)
    
    # Results
    pressure_data = Column(JSON, nullable=False)
    backwash_points = Column(JSON, default=[])
    fouling_rate = Column(Float, nullable=False)
    efficiency = Column(Float, nullable=False)
    recommendations = Column(JSON, default=[])
    confidence_score = Column(Float, nullable=False)
    
    # Metadata
    model_version = Column(String, default="1.0.0")
    prediction_accuracy = Column(Float, nullable=True)
    
    def to_dict(self):
        """Convert record to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "parameters": {
                "turbidity": self.turbidity,
                "ph": self.ph,
                "temperature": self.temperature,
                "flow_rate": self.flow_rate,
                "inlet_pressure": self.inlet_pressure
            },
            "prediction_parameters": {
                "fouling_status": self.fouling_status,
                "time_steps": self.time_steps,
                "pressure_threshold": self.pressure_threshold
            },
            "results": {
                "pressure_data": self.pressure_data,
                "backwash_points": self.backwash_points,
                "fouling_rate": self.fouling_rate,
                "efficiency": self.efficiency,
                "recommendations": self.recommendations,
                "confidence_score": self.confidence_score
            },
            "metadata": {
                "model_version": self.model_version,
                "prediction_accuracy": self.prediction_accuracy
            }
        }

class SystemConfig(Base):
    """Database model for system configuration"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSession(Base):
    """Database model for user sessions"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    preferences = Column(JSON, default={})

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def save_prediction_record(db, prediction_data: dict, parameters: dict, 
                          fouling_status: str, time_steps: int = 20, 
                          pressure_threshold: float = 7.0) -> PredictionRecord:
    """Save prediction record to database"""
    record = PredictionRecord(
        turbidity=parameters['turbidity'],
        ph=parameters['ph'],
        temperature=parameters['temperature'],
        flow_rate=parameters['flow_rate'],
        inlet_pressure=parameters['inlet_pressure'],
        fouling_status=fouling_status,
        time_steps=time_steps,
        pressure_threshold=pressure_threshold,
        pressure_data=prediction_data['pressure_data'],
        backwash_points=prediction_data['backwash_points'],
        fouling_rate=prediction_data['fouling_rate'],
        efficiency=prediction_data['efficiency'],
        recommendations=prediction_data['recommendations'],
        confidence_score=prediction_data.get('confidence_score', 0.9)
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_prediction_history(db, limit: int = 100, offset: int = 0, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None):
    """Get prediction history from database"""
    query = db.query(PredictionRecord)
    
    if start_date:
        query = query.filter(PredictionRecord.timestamp >= start_date)
    
    if end_date:
        query = query.filter(PredictionRecord.timestamp <= end_date)
    
    return query.order_by(PredictionRecord.timestamp.desc()).offset(offset).limit(limit).all()

def get_prediction_by_id(db, prediction_id: int) -> Optional[PredictionRecord]:
    """Get prediction record by ID"""
    return db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()

def update_system_config(db, key: str, value: str, description: str = None):
    """Update system configuration"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    if config:
        config.value = value
        if description:
            config.description = description
    else:
        config = SystemConfig(key=key, value=value, description=description)
        db.add(config)
    
    db.commit()
    return config

def get_system_config(db, key: str) -> Optional[str]:
    """Get system configuration value"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    return config.value if config else None 