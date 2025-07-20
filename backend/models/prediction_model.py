import numpy as np
from typing import Dict, List, Any, Optional
import random

class PredictionModel:
    """Intelligent UF Backwash Prediction Model"""
    
    def __init__(self):
        # Constants from frontend
        self.PRESSURE_THRESHOLD = 7.0
        self.PRESSURE_DROP_FACTOR = 0.5
        self.BACKWASH_DURATIONS = [140, 220, 360, 460]
        self.TIME_STEPS = 5
        
        # Fouling factors
        self.FOULING_FACTORS = {
            'clean': 1.0,
            'mild': 1.2,
            'moderate': 1.5,
            'severe': 1.8,
            'critical': 2.0
        }
        
        # Parameter ranges
        self.PARAM_RANGES = {
            'turbidity': {'min': 0.0, 'max': 2.0, 'default': 0.5},
            'ph': {'min': 4.0, 'max': 10.0, 'default': 7.0},
            'temperature': {'min': 15.0, 'max': 35.0, 'default': 25.0}
        }
    
    def predict(self, parameters: Dict[str, float], fouling_status: str = 'clean', 
                time_steps: int = 20, pressure_threshold: float = 7.0) -> Dict[str, Any]:
        """
        Predict pressure drop and backwash requirements
        
        Args:
            parameters: Water quality parameters
            fouling_status: Current fouling status
            time_steps: Number of time steps to predict
            pressure_threshold: Pressure threshold for backwash
            
        Returns:
            Dictionary containing prediction results
        """
        # Extract parameters
        turbidity = parameters.get('turbidity', 0.5)
        ph = parameters.get('ph', 7.0)
        temperature = parameters.get('temperature', 25.0)
        flow_rate = parameters.get('flow_rate', 20.0)
        inlet_pressure = parameters.get('inlet_pressure', 40.0)
        
        # Initialize pressure data
        pressure_data = []
        backwash_points = []
        
        # Initial pressure calculation
        current_pressure = 4.0 + (turbidity * 2.0)
        
        # Base trend calculation
        base_trend = 0.3 + (turbidity * 0.2)
        
        # Apply fouling factor
        fouling_factor = self.FOULING_FACTORS.get(fouling_status, 1.0)
        trend = base_trend * fouling_factor
        
        # Temperature effect
        trend *= (temperature / 25.0)
        
        # pH effect
        ph_factor = abs(ph - 7.0) * 0.1 + 1.0
        trend *= ph_factor
        
        # Flow rate effect
        flow_factor = (flow_rate / 20.0) * 0.2 + 0.8
        trend *= flow_factor
        
        last_backwash_step = -1
        
        for i in range(time_steps):
            pressure_data.append(current_pressure)
            
            # Check if backwash is needed
            if (current_pressure >= pressure_threshold and 
                (i - last_backwash_step) > 4):
                
                # Calculate backwash parameters
                backwash_params = self._calculate_backwash_params(
                    current_pressure, parameters, fouling_status
                )
                
                backwash_points.append({
                    'time_step': i,
                    'pressure': current_pressure,
                    'intensity': backwash_params['intensity'],
                    'duration': backwash_params['duration'],
                    'reason': 'pressure_threshold_exceeded'
                })
                
                last_backwash_step = i
                
                # Apply backwash effect
                current_pressure *= (1 - self.PRESSURE_DROP_FACTOR)
                
                # Calculate effectiveness
                intensity_factor = backwash_params['intensity'] / 10.0
                duration_factor = backwash_params['duration'] / 300.0
                effectiveness_factor = (intensity_factor + duration_factor) / 2.0
                
                # Adjust trend based on effectiveness
                trend *= (0.9 - (effectiveness_factor * 0.2))
                
                if effectiveness_factor > 1.2:
                    current_pressure *= 0.95
            
            # Add random variation and trend
            current_pressure += trend + (random.uniform(-0.1, 0.1))
            
            # Ensure pressure doesn't go below minimum
            current_pressure = max(current_pressure, 2.0)
        
        # Calculate fouling rate and efficiency
        fouling_rate = self._calculate_fouling_rate(pressure_data, parameters)
        efficiency = self._calculate_efficiency(pressure_data, backwash_points)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            parameters, fouling_status, backwash_points, efficiency
        )
        
        return {
            'pressure_data': [round(p, 2) for p in pressure_data],
            'backwash_points': backwash_points,
            'fouling_rate': round(fouling_rate, 3),
            'efficiency': round(efficiency, 3),
            'recommendations': recommendations,
            'confidence_score': 0.9
        }
    
    def predict_with_curves(self, base_parameters: Dict[str, float], 
                           curve_data: Dict[str, List[float]], 
                           fouling_status: str = 'clean', 
                           time_steps: int = 20) -> Dict[str, Any]:
        """
        Advanced prediction with time-varying parameters
        
        Args:
            base_parameters: Base water quality parameters
            curve_data: Time-varying parameter curves
            fouling_status: Current fouling status
            time_steps: Number of time steps to predict
            
        Returns:
            Dictionary containing prediction results
        """
        # Initialize with base parameters
        current_params = base_parameters.copy()
        pressure_data = []
        backwash_points = []
        
        # Get curve data
        turbidity_curve = curve_data.get('turbidity_curve', [base_parameters['turbidity']] * time_steps)
        ph_curve = curve_data.get('ph_curve', [base_parameters['ph']] * time_steps)
        temperature_curve = curve_data.get('temperature_curve', [base_parameters['temperature']] * time_steps)
        
        # Ensure curves have enough data points
        def pad_curve(curve, default_value, length):
            if len(curve) < length:
                return curve + [default_value] * (length - len(curve))
            return curve[:length]
        
        turbidity_curve = pad_curve(turbidity_curve, base_parameters['turbidity'], time_steps)
        ph_curve = pad_curve(ph_curve, base_parameters['ph'], time_steps)
        temperature_curve = pad_curve(temperature_curve, base_parameters['temperature'], time_steps)
        
        # Initial pressure
        current_pressure = 4.0 + (turbidity_curve[0] * 2.0)
        last_backwash_step = -1
        
        for i in range(time_steps):
            # Update parameters for this time step
            current_params['turbidity'] = turbidity_curve[i]
            current_params['ph'] = ph_curve[i]
            current_params['temperature'] = temperature_curve[i]
            
            pressure_data.append(current_pressure)
            
            # Calculate trend for current parameters
            trend = self._calculate_trend(current_params, fouling_status)
            
            # Check for backwash
            if (current_pressure >= self.PRESSURE_THRESHOLD and 
                (i - last_backwash_step) > 4):
                
                backwash_params = self._calculate_backwash_params(
                    current_pressure, current_params, fouling_status
                )
                
                backwash_points.append({
                    'time_step': i,
                    'pressure': current_pressure,
                    'intensity': backwash_params['intensity'],
                    'duration': backwash_params['duration'],
                    'reason': 'pressure_threshold_exceeded'
                })
                
                last_backwash_step = i
                current_pressure *= (1 - self.PRESSURE_DROP_FACTOR)
            
            # Update pressure
            current_pressure += trend + random.uniform(-0.1, 0.1)
            current_pressure = max(current_pressure, 2.0)
        
        # Calculate metrics
        fouling_rate = self._calculate_fouling_rate(pressure_data, current_params)
        efficiency = self._calculate_efficiency(pressure_data, backwash_points)
        recommendations = self._generate_recommendations(
            current_params, fouling_status, backwash_points, efficiency
        )
        
        return {
            'pressure_data': [round(p, 2) for p in pressure_data],
            'backwash_points': backwash_points,
            'fouling_rate': round(fouling_rate, 3),
            'efficiency': round(efficiency, 3),
            'recommendations': recommendations,
            'confidence_score': 0.85
        }
    
    def _calculate_backwash_params(self, pressure: float, parameters: Dict[str, float], 
                                 fouling_status: str) -> Dict[str, float]:
        """Calculate backwash intensity and duration"""
        fouling_factor = self.FOULING_FACTORS.get(fouling_status, 1.0)
        
        # Base intensity calculation
        base_intensity = (pressure - self.PRESSURE_THRESHOLD) * 1.5 * fouling_factor
        
        # Parameter effects
        ph_factor = abs(parameters['ph'] - 7.0) * 0.1 + 1.0
        temp_factor = parameters['temperature'] / 25.0
        turb_factor = (parameters['turbidity'] / 0.5) * 0.2 + 0.8
        
        intensity = base_intensity * ph_factor * temp_factor * turb_factor
        duration = random.choice(self.BACKWASH_DURATIONS)
        
        return {
            'intensity': round(intensity, 1),
            'duration': duration
        }
    
    def _calculate_trend(self, parameters: Dict[str, float], fouling_status: str) -> float:
        """Calculate pressure trend based on parameters"""
        base_trend = 0.3 + (parameters['turbidity'] * 0.2)
        fouling_factor = self.FOULING_FACTORS.get(fouling_status, 1.0)
        trend = base_trend * fouling_factor
        
        # Temperature effect
        trend *= (parameters['temperature'] / 25.0)
        
        # pH effect
        ph_factor = abs(parameters['ph'] - 7.0) * 0.1 + 1.0
        trend *= ph_factor
        
        return trend
    
    def _calculate_fouling_rate(self, pressure_data: List[float], 
                               parameters: Dict[str, float]) -> float:
        """Calculate fouling rate based on pressure increase"""
        if len(pressure_data) < 2:
            return 0.0
        
        # Calculate average rate of pressure increase
        pressure_changes = [pressure_data[i] - pressure_data[i-1] 
                          for i in range(1, len(pressure_data))]
        
        # Filter out negative changes (backwash effects)
        positive_changes = [change for change in pressure_changes if change > 0]
        
        if not positive_changes:
            return 0.0
        
        return sum(positive_changes) / len(positive_changes)
    
    def _calculate_efficiency(self, pressure_data: List[float], 
                            backwash_points: List[Dict]) -> float:
        """Calculate system efficiency"""
        if not pressure_data:
            return 0.0
        
        # Base efficiency on pressure stability
        pressure_variance = np.var(pressure_data)
        base_efficiency = max(0.5, 1.0 - (pressure_variance / 10.0))
        
        # Adjust based on backwash frequency
        if len(backwash_points) > 0:
            avg_backwash_interval = len(pressure_data) / len(backwash_points)
            if avg_backwash_interval < 5:
                base_efficiency *= 0.9  # Too frequent backwash
            elif avg_backwash_interval > 15:
                base_efficiency *= 0.95  # Infrequent backwash
        
        return min(1.0, base_efficiency)
    
    def _generate_recommendations(self, parameters: Dict[str, float], 
                                fouling_status: str, backwash_points: List[Dict], 
                                efficiency: float) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        # pH recommendations
        if abs(parameters['ph'] - 7.0) > 1.0:
            recommendations.append("Consider adjusting pH closer to neutral (7.0) for optimal performance")
        
        # Temperature recommendations
        if parameters['temperature'] > 30.0:
            recommendations.append("High temperature detected - monitor fouling rate closely")
        elif parameters['temperature'] < 20.0:
            recommendations.append("Low temperature may reduce system efficiency")
        
        # Turbidity recommendations
        if parameters['turbidity'] > 1.0:
            recommendations.append("High turbidity detected - consider pre-treatment")
        
        # Fouling status recommendations
        if fouling_status in ['severe', 'critical']:
            recommendations.append("Severe fouling detected - consider chemical cleaning")
        
        # Efficiency recommendations
        if efficiency < 0.7:
            recommendations.append("System efficiency is low - review operational parameters")
        
        # Backwash frequency recommendations
        if len(backwash_points) > 0:
            avg_interval = 20 / len(backwash_points)  # Assuming 20 time steps
            if avg_interval < 5:
                recommendations.append("Backwash frequency is high - consider optimizing parameters")
            elif avg_interval > 15:
                recommendations.append("Backwash frequency is low - monitor pressure closely")
        
        if not recommendations:
            recommendations.append("System operating within optimal parameters")
        
        return recommendations 