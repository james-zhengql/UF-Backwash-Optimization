# Intelligent UF Backwash System

A comprehensive web application for predicting pressure drop and backwash requirements in ultrafiltration membrane systems. The system combines a modern frontend interface with a powerful backend API to provide intelligent predictions and recommendations.

## 🚀 Features

### Frontend
- **Interactive Parameter Input**: Real-time input validation for water quality parameters
- **Dynamic Charts**: Interactive pressure prediction charts with Chart.js
- **Backwash Point Visualization**: Highlighted backwash points with detailed information
- **Responsive Design**: Modern Bootstrap-based UI that works on all devices
- **Curve Editors**: Advanced parameter curve editing for time-varying inputs

### Backend
- **RESTful API**: FastAPI-based backend with comprehensive endpoints
- **Intelligent Prediction**: Advanced algorithms for pressure and backwash prediction
- **Parameter Validation**: Robust input validation and sanitization
- **Database Storage**: SQLAlchemy-based data persistence
- **Real-time Processing**: Fast prediction generation with confidence scores

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 14 or higher (for frontend dependencies)
- **Memory**: 2GB RAM minimum
- **Storage**: 100MB free space

## 🛠️ Installation

### Quick Start (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd intelligent-uf-backwash
   ```

2. **Run the startup script**
   ```bash
   python start_system.py
   ```

   This will automatically:
   - Create a Python virtual environment
   - Install all dependencies
   - Start both frontend and backend servers
   - Open the application in your browser

### Manual Installation

#### Backend Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start backend server**
   ```bash
   python run.py
   ```

#### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   npm install
   ```

2. **Start frontend server**
   ```bash
   python -m http.server 8080
   ```

## 🌐 Access Points

Once the system is running:

- **Frontend Application**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System health check |
| `/api/model/info` | GET | Get model information and parameters |
| `/api/predict` | POST | Basic prediction endpoint |
| `/api/predict/advanced` | POST | Advanced prediction with curves |
| `/api/history` | GET | Get prediction history |

### Example API Usage

#### Basic Prediction
```bash
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

#### Advanced Prediction with Curves
```bash
curl -X POST http://localhost:8000/api/predict/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "turbidity": 0.5,
      "ph": 7.0,
      "temperature": 25.0,
      "flow_rate": 20.0,
      "inlet_pressure": 40.0
    },
    "curve_data": {
      "turbidity_curve": [0.5, 0.6, 0.7, 0.8, 0.9],
      "ph_curve": [7.0, 7.1, 7.2, 7.3, 7.4],
      "temperature_curve": [25.0, 25.5, 26.0, 26.5, 27.0]
    },
    "fouling_status": "mild"
  }'
```

## 🧪 Testing

### API Testing
```bash
python test_api.py
```

### Manual Testing
1. Open http://localhost:8080
2. Enter water quality parameters
3. Click "Forecast" button
4. View prediction results and charts
5. Click on backwash points for detailed information

## 📁 Project Structure

```
intelligent-uf-backwash/
├── backend/                 # Backend API
│   ├── main.py             # FastAPI application
│   ├── models/             # Database and prediction models
│   ├── schemas/            # Pydantic data models
│   └── utils/              # Validation utilities
├── css/                    # Frontend styles
├── js/                     # Frontend JavaScript
├── images/                 # Static images
├── index.html              # Main frontend page
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
├── run.py                 # Backend startup script
├── start_system.py        # Complete system startup
└── test_api.py           # API testing script
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./uf_backwash.db` | Database connection string |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Backend port |
| `RELOAD` | `true` | Enable auto-reload |

### Parameter Ranges

| Parameter | Min | Max | Unit | Default |
|-----------|-----|-----|------|---------|
| Turbidity | 0.0 | 2.0 | NTU | 0.5 |
| pH | 4.0 | 10.0 | - | 7.0 |
| Temperature | 15.0 | 35.0 | °C | 25.0 |
| Flow Rate | 10.0 | 50.0 | GPM | 20.0 |
| Inlet Pressure | 20.0 | 80.0 | PSIG | 40.0 |

## 🚀 Deployment

### Development
```bash
python start_system.py
```

### Production
1. Set `RELOAD=false`
2. Use production ASGI server (Gunicorn)
3. Configure reverse proxy (nginx)
4. Set up SSL/TLS certificates
5. Use production database (PostgreSQL)

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at http://localhost:8000/docs
- Review the backend documentation in `README_backend.md`
- Open an issue on GitHub

## 🔄 Version History

- **v1.0.0**: Initial release with basic prediction functionality
- **v1.1.0**: Added advanced curve-based predictions
- **v1.2.0**: Enhanced UI and API documentation

---

**Note**: This system is designed for educational and research purposes. For production use in water treatment facilities, additional validation and safety measures should be implemented.
