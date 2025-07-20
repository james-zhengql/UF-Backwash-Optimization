# Intelligent UF Backwash API Backend

This is the backend API for the Intelligent UF Backwash prediction system. It provides RESTful endpoints for predicting pressure drop and backwash requirements in ultrafiltration membrane systems.

## Features

- **Pressure Prediction**: Predict pressure changes over time based on water quality parameters
- **Backwash Optimization**: Calculate optimal backwash timing and parameters
- **Parameter Validation**: Comprehensive input validation and sanitization
- **Database Storage**: Store prediction history and system configurations
- **RESTful API**: Clean, documented API endpoints
- **CORS Support**: Cross-origin resource sharing enabled

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API information
- `GET /api/model/info` - Get model information and supported parameters
- `POST /api/predict` - Main prediction endpoint
- `POST /api/predict/advanced` - Advanced prediction with curve data
- `GET /api/history` - Get prediction history
- `GET /api/health` - Health check endpoint

### Request/Response Examples

#### Basic Prediction Request
```json
{
  "parameters": {
    "turbidity": 0.5,
    "ph": 7.0,
    "temperature": 25.0,
    "flow_rate": 20.0,
    "inlet_pressure": 40.0
  },
  "fouling_status": "clean",
  "time_steps": 20,
  "pressure_threshold": 7.0
}
```

#### Prediction Response
```json
{
  "success": true,
  "prediction_data": {
    "pressure_data": [4.2, 4.5, 4.8, 5.1, 5.4, 5.7, 6.0, 6.3, 6.6, 6.9, 7.2, 4.1, 4.4, 4.7, 5.0, 5.3, 5.6, 5.9, 6.2, 6.5],
    "backwash_points": [
      {
        "time_step": 10,
        "pressure": 7.2,
        "intensity": 8.5,
        "duration": 220,
        "reason": "pressure_threshold_exceeded"
      }
    ],
    "fouling_rate": 0.15,
    "efficiency": 0.85,
    "recommendations": [
      "System operating within optimal parameters"
    ]
  },
  "metadata": {
    "model_version": "1.0.0",
    "prediction_timestamp": "2024-01-15T10:30:00Z",
    "confidence_score": 0.9
  }
}
```

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional)
   ```bash
   export DATABASE_URL="sqlite:///./uf_backwash.db"
   export HOST="0.0.0.0"
   export PORT="8000"
   export RELOAD="true"
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Project Structure

```
backend/
├── __init__.py
├── main.py                 # FastAPI application
├── models/
│   ├── __init__.py
│   ├── prediction_model.py # Core prediction algorithm
│   └── database.py        # Database models and operations
├── schemas/
│   ├── __init__.py
│   └── prediction.py      # Pydantic data models
└── utils/
    ├── __init__.py
    └── validators.py      # Input validation utilities
```

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string (default: SQLite)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload (default: true)

### Database

The application uses SQLAlchemy with support for:
- SQLite (default)
- PostgreSQL
- MySQL

To use PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:password@localhost/uf_backwash"
```

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## Testing

### Manual Testing

Test the API using curl:

```bash
# Health check
curl http://localhost:8000/api/health

# Get model info
curl http://localhost:8000/api/model/info

# Make prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "turbidity": 0.5,
      "ph": 7.0,
      "temperature": 25.0,
      "flow_rate": 20.0,
      "inlet_pressure": 40.0
    },
    "fouling_status": "clean",
    "time_steps": 20
  }'
```

### Automated Testing

Run tests with pytest:
```bash
pytest tests/
```

## Development

### Adding New Endpoints

1. Add the endpoint to `backend/main.py`
2. Create corresponding Pydantic models in `backend/schemas/`
3. Add validation in `backend/utils/validators.py`
4. Update documentation

### Modifying Prediction Algorithm

1. Edit `backend/models/prediction_model.py`
2. Test with different parameter combinations
3. Update model version in responses

### Database Migrations

For schema changes:
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Deployment

### Docker

Create a Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

### Production

For production deployment:
1. Set `RELOAD=false`
2. Use a production ASGI server like Gunicorn
3. Configure proper database (PostgreSQL recommended)
4. Set up reverse proxy (nginx)
5. Configure SSL/TLS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 