from typing import Dict, Any, List
import re

def validate_parameters(parameters: Dict[str, float]) -> Dict[str, Any]:
    """
    Validate input parameters for prediction
    
    Args:
        parameters: Dictionary of water quality parameters
        
    Returns:
        Dictionary with validation result
    """
    # Parameter ranges
    param_ranges = {
        'turbidity': {'min': 0.0, 'max': 2.0, 'unit': 'NTU'},
        'ph': {'min': 4.0, 'max': 10.0, 'unit': ''},
        'temperature': {'min': 15.0, 'max': 35.0, 'unit': '°C'},
        'flow_rate': {'min': 10.0, 'max': 50.0, 'unit': 'GPM'},
        'inlet_pressure': {'min': 20.0, 'max': 80.0, 'unit': 'PSIG'}
    }
    
    # Required parameters
    required_params = ['turbidity', 'ph', 'temperature', 'flow_rate', 'inlet_pressure']
    
    # Check for required parameters
    for param in required_params:
        if param not in parameters:
            return {
                'valid': False,
                'error': f'Missing required parameter: {param}',
                'details': {
                    'parameter': param,
                    'required': True
                }
            }
    
    # Validate each parameter
    for param, value in parameters.items():
        if param not in param_ranges:
            return {
                'valid': False,
                'error': f'Unknown parameter: {param}',
                'details': {
                    'parameter': param,
                    'valid_parameters': list(param_ranges.keys())
                }
            }
        
        # Check if value is numeric
        if not isinstance(value, (int, float)):
            return {
                'valid': False,
                'error': f'Parameter {param} must be numeric',
                'details': {
                    'parameter': param,
                    'value': value,
                    'type': type(value).__name__
                }
            }
        
        # Check range
        param_range = param_ranges[param]
        if value < param_range['min'] or value > param_range['max']:
            return {
                'valid': False,
                'error': f'Parameter {param} value {value} is out of range',
                'details': {
                    'parameter': param,
                    'value': value,
                    'valid_range': [param_range['min'], param_range['max']],
                    'unit': param_range['unit']
                }
            }
    
    return {'valid': True}

def validate_fouling_status(fouling_status: str) -> Dict[str, Any]:
    """
    Validate fouling status parameter
    
    Args:
        fouling_status: Fouling status string
        
    Returns:
        Dictionary with validation result
    """
    valid_statuses = ['clean', 'mild', 'moderate', 'severe', 'critical']
    
    if fouling_status not in valid_statuses:
        return {
            'valid': False,
            'error': f'Invalid fouling status: {fouling_status}',
            'details': {
                'provided_status': fouling_status,
                'valid_statuses': valid_statuses
            }
        }
    
    return {'valid': True}

def validate_time_steps(time_steps: int) -> Dict[str, Any]:
    """
    Validate time steps parameter
    
    Args:
        time_steps: Number of time steps
        
    Returns:
        Dictionary with validation result
    """
    if not isinstance(time_steps, int):
        return {
            'valid': False,
            'error': 'Time steps must be an integer',
            'details': {
                'provided_type': type(time_steps).__name__,
                'required_type': 'int'
            }
        }
    
    if time_steps < 1 or time_steps > 50:
        return {
            'valid': False,
            'error': f'Time steps {time_steps} is out of range',
            'details': {
                'value': time_steps,
                'valid_range': [1, 50]
            }
        }
    
    return {'valid': True}

def validate_pressure_threshold(threshold: float) -> Dict[str, Any]:
    """
    Validate pressure threshold parameter
    
    Args:
        threshold: Pressure threshold value
        
    Returns:
        Dictionary with validation result
    """
    if not isinstance(threshold, (int, float)):
        return {
            'valid': False,
            'error': 'Pressure threshold must be numeric',
            'details': {
                'provided_type': type(threshold).__name__,
                'required_type': 'float'
            }
        }
    
    if threshold < 1.0 or threshold > 15.0:
        return {
            'valid': False,
            'error': f'Pressure threshold {threshold} is out of range',
            'details': {
                'value': threshold,
                'valid_range': [1.0, 15.0],
                'unit': 'PSIG'
            }
        }
    
    return {'valid': True}

def validate_curve_data(curve_data: Dict[str, List[float]]) -> Dict[str, Any]:
    """
    Validate curve data for advanced predictions
    
    Args:
        curve_data: Dictionary of curve data
        
    Returns:
        Dictionary with validation result
    """
    valid_curves = ['turbidity_curve', 'ph_curve', 'temperature_curve']
    
    for curve_name, curve_values in curve_data.items():
        if curve_name not in valid_curves:
            return {
                'valid': False,
                'error': f'Unknown curve: {curve_name}',
                'details': {
                    'provided_curve': curve_name,
                    'valid_curves': valid_curves
                }
            }
        
        # Check if curve values are numeric
        for i, value in enumerate(curve_values):
            if not isinstance(value, (int, float)):
                return {
                    'valid': False,
                    'error': f'Curve {curve_name} contains non-numeric value at index {i}',
                    'details': {
                        'curve': curve_name,
                        'index': i,
                        'value': value,
                        'type': type(value).__name__
                    }
                }
        
        # Check curve length
        if len(curve_values) < 1:
            return {
                'valid': False,
                'error': f'Curve {curve_name} is empty',
                'details': {
                    'curve': curve_name,
                    'length': len(curve_values)
                }
            }
    
    return {'valid': True}

def validate_prediction_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete prediction request
    
    Args:
        request_data: Complete request data
        
    Returns:
        Dictionary with validation result
    """
    # Check required fields
    required_fields = ['parameters', 'fouling_status']
    for field in required_fields:
        if field not in request_data:
            return {
                'valid': False,
                'error': f'Missing required field: {field}',
                'details': {
                    'missing_field': field,
                    'required_fields': required_fields
                }
            }
    
    # Validate parameters
    param_validation = validate_parameters(request_data['parameters'])
    if not param_validation['valid']:
        return param_validation
    
    # Validate fouling status
    fouling_validation = validate_fouling_status(request_data['fouling_status'])
    if not fouling_validation['valid']:
        return fouling_validation
    
    # Validate optional fields
    if 'time_steps' in request_data:
        time_validation = validate_time_steps(request_data['time_steps'])
        if not time_validation['valid']:
            return time_validation
    
    if 'pressure_threshold' in request_data:
        threshold_validation = validate_pressure_threshold(request_data['pressure_threshold'])
        if not threshold_validation['valid']:
            return threshold_validation
    
    # Validate curve data if present
    if 'curve_data' in request_data:
        curve_validation = validate_curve_data(request_data['curve_data'])
        if not curve_validation['valid']:
            return curve_validation
    
    return {'valid': True}

def sanitize_parameters(parameters: Dict[str, float]) -> Dict[str, float]:
    """
    Sanitize and round parameter values
    
    Args:
        parameters: Raw parameter values
        
    Returns:
        Sanitized parameter values
    """
    sanitized = {}
    
    for param, value in parameters.items():
        # Convert to float and round to 2 decimal places
        sanitized[param] = round(float(value), 2)
    
    return sanitized 