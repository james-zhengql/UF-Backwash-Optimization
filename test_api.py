#!/usr/bin/env python3
"""
Test script for the Intelligent UF Backwash API
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_model_info():
    """Test model info endpoint"""
    print("Testing model info...")
    response = requests.get(f"{BASE_URL}/api/model/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_basic_prediction():
    """Test basic prediction endpoint"""
    print("Testing basic prediction...")
    
    payload = {
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
    
    response = requests.post(f"{BASE_URL}/api/predict", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Prediction successful!")
        print(f"Pressure data points: {len(result['prediction_data']['pressure_data'])}")
        print(f"Backwash points: {len(result['prediction_data']['backwash_points'])}")
        print(f"Fouling rate: {result['prediction_data']['fouling_rate']}")
        print(f"Efficiency: {result['prediction_data']['efficiency']}")
        print(f"Recommendations: {result['prediction_data']['recommendations']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_advanced_prediction():
    """Test advanced prediction with curve data"""
    print("Testing advanced prediction...")
    
    payload = {
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
        "fouling_status": "mild",
        "time_steps": 20
    }
    
    response = requests.post(f"{BASE_URL}/api/predict/advanced", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Advanced prediction successful!")
        print(f"Uses curve data: {result['metadata']['uses_curve_data']}")
        print(f"Pressure data points: {len(result['prediction_data']['pressure_data'])}")
    else:
        print(f"Error: {response.text}")
    print()

def test_invalid_parameters():
    """Test parameter validation"""
    print("Testing parameter validation...")
    
    # Test invalid turbidity
    payload = {
        "parameters": {
            "turbidity": 5.0,  # Out of range
            "ph": 7.0,
            "temperature": 25.0,
            "flow_rate": 20.0,
            "inlet_pressure": 40.0
        },
        "fouling_status": "clean"
    }
    
    response = requests.post(f"{BASE_URL}/api/predict", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_history():
    """Test history endpoint"""
    print("Testing history endpoint...")
    response = requests.get(f"{BASE_URL}/api/history")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all tests"""
    print("Starting API tests...")
    print("=" * 50)
    
    try:
        test_health_check()
        test_model_info()
        test_basic_prediction()
        test_advanced_prediction()
        test_invalid_parameters()
        test_history()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python run.py")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main() 