// Initialize curve editors and charts
let pressureChart = null;
let curveEditors = {
  turb: null,
  ph: null,
  temp: null
};

// API configuration
const API_BASE_URL = 'http://localhost:8000';
const API_ENDPOINTS = {
  predict: '/api/predict',
  predictAdvanced: '/api/predict/advanced',
  modelInfo: '/api/model/info',
  health: '/api/health',
  history: '/api/history'
};

// Constants
const PRESSURE_THRESHOLD = 7.0;
const PRESSURE_DROP_FACTOR = 0.5;
const BACKWASH_DURATIONS = [140, 220, 360, 460];
const TIME_STEPS = 5;

// Parameter ranges for curve editors
const PARAM_RANGES = {
  turb: { min: 0, max: 2.0, default: 0.5 },
  ph: { min: 4, max: 10, default: 7.0 },
  temp: { min: 15, max: 35, default: 25.0 }
};

// Fouling status mappings
const FOULING_FACTORS = {
  clean: 1.0,
  mild: 1.2,
  moderate: 1.5,
  severe: 1.8,
  critical: 2.0
};

// API communication functions
async function callAPI(endpoint, data = null) {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
      method: data ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      body: data ? JSON.stringify(data) : undefined
    };

    const response = await fetch(url, options);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

async function getModelInfo() {
  try {
    const info = await callAPI(API_ENDPOINTS.modelInfo);
    console.log('Model info:', info);
    return info;
  } catch (error) {
    console.error('Failed to get model info:', error);
    return null;
  }
}

async function predictBackwash(parameters, foulingStatus = 'clean', timeSteps = 20, pressureThreshold = 7.0) {
  try {
    const payload = {
      parameters: {
        turbidity: parameters.turb,
        ph: parameters.ph,
        temperature: parameters.temp,
        flow_rate: parameters.flow || 20.0,
        inlet_pressure: parameters.inletPressure || 40.0
      },
      fouling_status: foulingStatus,
      time_steps: timeSteps,
      pressure_threshold: pressureThreshold
    };

    const result = await callAPI(API_ENDPOINTS.predict, payload);
    console.log('Prediction result:', result);
    return result;
  } catch (error) {
    console.error('Prediction failed:', error);
    throw error;
  }
}

async function predictAdvanced(baseParameters, curveData, foulingStatus = 'clean', timeSteps = 20) {
  try {
    const payload = {
      parameters: {
        turbidity: baseParameters.turb,
        ph: baseParameters.ph,
        temperature: baseParameters.temp,
        flow_rate: baseParameters.flow || 20.0,
        inlet_pressure: baseParameters.inletPressure || 40.0
      },
      curve_data: curveData,
      fouling_status: foulingStatus,
      time_steps: timeSteps
    };

    const result = await callAPI(API_ENDPOINTS.predictAdvanced, payload);
    console.log('Advanced prediction result:', result);
    return result;
  } catch (error) {
    console.error('Advanced prediction failed:', error);
    throw error;
  }
}

// Initialize curve editor
function initializeCurveEditor(type) {
  const editor = document.getElementById(`${type}-curve-editor`);
  if (!editor) return null;

  // Clear any existing content
  editor.innerHTML = '';
  
  const points = [];
  const container = editor.getBoundingClientRect();
  
  // Add axis labels
  const xAxis = document.createElement('div');
  xAxis.className = 'curve-editor-axis x-axis';
  xAxis.textContent = 'Time Step';
  editor.appendChild(xAxis);
  
  const yAxis = document.createElement('div');
  yAxis.className = 'curve-editor-axis y-axis';
  yAxis.textContent = type === 'turb' ? 'NTU' : type === 'ph' ? 'pH' : '°C';
  editor.appendChild(yAxis);
  
  // Create initial points
  for (let i = 0; i < TIME_STEPS; i++) {
    const point = document.createElement('div');
    point.className = 'curve-point';
    point.dataset.index = i;
    
    // Position point with default value
    const x = (i / (TIME_STEPS - 1)) * (container.width - 20) + 10;
    const range = PARAM_RANGES[type];
    const defaultY = container.height - ((range.default - range.min) / (range.max - range.min)) * container.height;
    
    point.style.left = `${x}px`;
    point.style.top = `${defaultY}px`;
    
    editor.appendChild(point);
    points.push(point);
    
    // Add drag functionality
    makeDraggable(point, editor, type);
  }
  
  // Create connecting lines
  for (let i = 0; i < TIME_STEPS - 1; i++) {
    const line = document.createElement('div');
    line.className = 'curve-line';
    editor.appendChild(line);
  }
  
  updateLines(editor);
  return { editor, points };
}

// Make point draggable
function makeDraggable(point, editor, type) {
  let isDragging = false;
  let currentX;
  let currentY;
  
  point.addEventListener('mousedown', e => {
    isDragging = true;
    point.style.cursor = 'grabbing';
    
    // Calculate offset of mouse from point center
    const rect = point.getBoundingClientRect();
    currentX = e.clientX - rect.left;
    currentY = e.clientY - rect.top;
    
    e.preventDefault();
  });
  
  document.addEventListener('mousemove', e => {
    if (!isDragging) return;
    
    const container = editor.getBoundingClientRect();
    const index = parseInt(point.dataset.index);
    
    // Calculate boundaries
    const minX = container.left + 10;
    const maxX = container.right - 10;
    const minY = container.top + 10;
    const maxY = container.bottom - 10;
    
    // Restrict horizontal movement based on point index
    const stepWidth = (container.width - 20) / (TIME_STEPS - 1);
    const allowedX = container.left + (stepWidth * index) + 10;
    
    // Update position
    let newX = allowedX;
    let newY = Math.min(Math.max(e.clientY - currentY, minY), maxY);
    
    point.style.left = `${newX - container.left}px`;
    point.style.top = `${newY - container.top}px`;
    
    // Update lines
    updateLines(editor);
    
    // Update tooltip
    updateTooltip(point, type);
  });
  
  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      point.style.cursor = 'move';
    }
  });
}

// Update connecting lines
function updateLines(editor) {
  const points = Array.from(editor.getElementsByClassName('curve-point'));
  const lines = Array.from(editor.getElementsByClassName('curve-line'));
  
  points.forEach((point, i) => {
    if (i < points.length - 1) {
      const line = lines[i];
      const nextPoint = points[i + 1];
      
      const x1 = parseInt(point.style.left);
      const y1 = parseInt(point.style.top);
      const x2 = parseInt(nextPoint.style.left);
      const y2 = parseInt(nextPoint.style.top);
      
      const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
      const angle = Math.atan2(y2 - y1, x2 - x1);
      
      line.style.width = `${length}px`;
      line.style.left = `${x1}px`;
      line.style.top = `${y1}px`;
      line.style.transform = `rotate(${angle}rad)`;
    }
  });
}

// Update point tooltip
function updateTooltip(point, type) {
  const container = point.parentElement.getBoundingClientRect();
  const pointRect = point.getBoundingClientRect();
  const range = PARAM_RANGES[type];
  
  // Calculate value based on position
  const normalizedY = 1 - ((pointRect.top + pointRect.height/2 - container.top) / container.height);
  const value = range.min + (normalizedY * (range.max - range.min));
  
  point.title = `Time Step ${parseInt(point.dataset.index) + 1}: ${value.toFixed(1)} ${type === 'turb' ? 'NTU' : type === 'ph' ? '' : '°C'}`;
}

// Get values from curve editor
function getCurveValues(type) {
  const editor = document.getElementById(`${type}-curve-editor`);
  const points = Array.from(editor.getElementsByClassName('curve-point'));
  const container = editor.getBoundingClientRect();
  const range = PARAM_RANGES[type];
  
  return points.map(point => {
    const pointRect = point.getBoundingClientRect();
    const normalizedY = 1 - ((pointRect.top + pointRect.height/2 - container.top) / container.height);
    return range.min + (normalizedY * (range.max - range.min));
  });
}

// Create a chart
function createChart(ctx, label, data, type = 'default') {
  if (!ctx) {
    console.error('Canvas context is null for', label);
    return null;
  }
  
  const labels = Array.from({length: data.data.length}, (_, i) => i + 1);
  
  let chartConfig = {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: type === 'pressure' ? data.data : data,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.3,
        pointRadius: (context) => {
          if (type === 'pressure' && data.backwashPoints) {
            const isBackwashPoint = data.backwashPoints.some(point => 
              point.time_step === context.dataIndex
            );
            return isBackwashPoint ? 8 : 5;
          }
          return 5;
        },
        pointHoverRadius: 8,
        pointBackgroundColor: (context) => {
          if (type === 'pressure' && data.backwashPoints) {
            const isBackwashPoint = data.backwashPoints.some(point => 
              point.time_step === context.dataIndex
            );
            return isBackwashPoint ? 'rgb(255, 99, 132)' : 'rgb(75, 192, 192)';
          }
          return 'rgb(75, 192, 192)';
        },
        pointBorderColor: (context) => {
          if (type === 'pressure' && data.backwashPoints) {
            const isBackwashPoint = data.backwashPoints.some(point => 
              point.time_step === context.dataIndex
            );
            return isBackwashPoint ? 'rgb(255, 99, 132)' : 'rgb(75, 192, 192)';
          }
          return 'rgb(75, 192, 192)';
        }
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          title: {
            display: true,
            text: 'Time Step'
          },
          offset: false,
          grid: {
            offset: false
          },
          ticks: {
            stepSize: 1
          }
        },
        y: {
          title: {
            display: true,
            text: type === 'pressure' ? 'Pressure (PSIG)' : 'Predicted Value'
          },
          min: 0,
          max: 15,
          grid: {
            drawBorder: true,
            color: function(context) {
              if (context.tick.value > 10) {
                return 'rgba(0,0,0,0)';
              }
              return 'rgba(0,0,0,0.1)';
            }
          },
          ticks: {
            callback: function(value) {
              if (value > 10) {
                return '';
              }
              return value;
            }
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              const value = context.parsed.y.toFixed(2);
              if (type === 'pressure') {
                const backwashPoint = data.backwashPoints.find(point => 
                  point.time_step === context.dataIndex
                );
                if (backwashPoint) {
                  return `Pressure: ${value} PSIG (Backwash Point)`;
                }
                return `Pressure: ${value} PSIG`;
              }
              return `Value: ${value}`;
            }
          }
        }
      },
      onClick: (event, elements) => {
        if (!elements || elements.length === 0) return;
        
        const element = elements[0];
        const dataIndex = element.index;
        
        if (type === 'pressure') {
          const backwashPoint = data.backwashPoints.find(point => 
            point.time_step === dataIndex
          );
          
          if (backwashPoint) {
            showBackwashModal(backwashPoint);
          }
        }
      }
    }
  };
  
  if (type === 'pressure' && data.backwashPoints && data.backwashPoints.length > 0) {
    chartConfig.options.plugins.annotation = {
      annotations: data.backwashPoints.reduce((acc, point, index) => {
        acc[`backwashPoint${index}`] = {
          type: 'point',
          xValue: point.time_step,
          yValue: point.pressure,
          backgroundColor: 'rgba(255, 99, 132, 0.9)',
          borderColor: 'white',
          borderWidth: 2,
          radius: 8
        };
        return acc;
      }, {})
    };
  }
  
  return new Chart(ctx, chartConfig);
}

// Show backwash modal
function showBackwashModal(backwashPoint) {
  // Remove existing modal if any
  const existingModal = document.getElementById('backwashModal');
  if (existingModal) {
    existingModal.remove();
  }
  
  // Create modal HTML
  const modalHTML = `
    <div class="modal fade" id="backwashModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Backwash Point Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="backwash-info">
              <div class="info-item">
                <span class="info-label" data-label="Time Step">Time Step</span>
                <span class="info-value">${backwashPoint.time_step + 1}</span>
              </div>
              <div class="info-item">
                <span class="info-label" data-label="Pressure">Pressure</span>
                <span class="info-value">${backwashPoint.pressure.toFixed(2)} PSIG</span>
              </div>
              <div class="info-item">
                <span class="info-label" data-label="Intensity">Backwash Intensity</span>
                <span class="info-value">${backwashPoint.intensity} W</span>
              </div>
              <div class="info-item">
                <span class="info-label" data-label="Duration">Backwash Duration</span>
                <span class="info-value">${backwashPoint.duration} s</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="modal-btn modal-btn-primary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to document
  document.body.insertAdjacentHTML('beforeend', modalHTML);
  
  // Initialize and show modal
  const modal = new bootstrap.Modal(document.getElementById('backwashModal'));
  modal.show();
}

// Show loading indicator
function showLoading() {
  const forecastBtn = document.getElementById('forecast-btn');
  const originalText = forecastBtn.textContent;
  forecastBtn.textContent = 'Predicting...';
  forecastBtn.disabled = true;
  return () => {
    forecastBtn.textContent = originalText;
    forecastBtn.disabled = false;
  };
}

// Show error message
function showError(message) {
  // Create error alert
  const alertHTML = `
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Error:</strong> ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;
  
  // Insert at the top of the main container
  const mainContainer = document.querySelector('main.container');
  mainContainer.insertAdjacentHTML('afterbegin', alertHTML);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    const alert = document.querySelector('.alert');
    if (alert) {
      alert.remove();
    }
  }, 5000);
}

// Initialize curve editors on page load
document.addEventListener('DOMContentLoaded', async () => {
  // Initialize curve editors
  Object.keys(curveEditors).forEach(type => {
    curveEditors[type] = initializeCurveEditor(type);
  });
  
  // Test API connection
  try {
    const modelInfo = await getModelInfo();
    if (modelInfo) {
      console.log('API connection successful');
    }
  } catch (error) {
    console.warn('API connection failed, using local prediction:', error);
  }
  
  // Add forecast button handler
  document.getElementById('forecast-btn').addEventListener('click', async () => {
    const hideLoading = showLoading();
    
    try {
      // Get current values from input fields
      const params = {
        turb: parseFloat(document.getElementById('turb-input').value),
        ph: parseFloat(document.getElementById('ph-input').value),
        temp: parseFloat(document.getElementById('temp-input').value),
        flow: parseFloat(document.getElementById('flow-input').value),
        inletPressure: parseFloat(document.getElementById('inlet-pressure-input').value)
      };
      
      // Try API prediction first
      let predictionResult;
      try {
        predictionResult = await predictBackwash(params, 'clean', 20, 7.0);
        
        if (predictionResult.success) {
          // Use API result
          const pressureData = {
            data: predictionResult.prediction_data.pressure_data,
            backwashPoints: predictionResult.prediction_data.backwash_points
          };
          
          // Show chart section
          const chartSection = document.getElementById('chart-section');
          chartSection.style.display = 'block';
          
          // Update or create pressure chart
          const ctx = document.getElementById('pressureChart').getContext('2d');
          if (pressureChart) {
            pressureChart.destroy();
          }
          
          pressureChart = createChart(ctx, 'Pressure Drop', pressureData, 'pressure');
          
          // Show recommendations if available
          if (predictionResult.prediction_data.recommendations) {
            console.log('Recommendations:', predictionResult.prediction_data.recommendations);
          }
          
        } else {
          throw new Error('API returned unsuccessful response');
        }
        
      } catch (apiError) {
        console.warn('API prediction failed, using local fallback:', apiError);
        
        // Fallback to local prediction
        const pressureData = generateSampleData('pressure', params);
        
        // Show chart section
        const chartSection = document.getElementById('chart-section');
        chartSection.style.display = 'block';
        
        // Update or create pressure chart
        const ctx = document.getElementById('pressureChart').getContext('2d');
        if (pressureChart) {
          pressureChart.destroy();
        }
        
        pressureChart = createChart(ctx, 'Pressure Drop', pressureData, 'pressure');
      }
      
      // Scroll to chart
      setTimeout(() => {
        const chartSection = document.getElementById('chart-section');
        chartSection.scrollIntoView({ 
          behavior: 'smooth',
          block: 'center'
        });
      }, 100);
      
    } catch (error) {
      console.error('Prediction failed:', error);
      showError('Failed to generate prediction. Please try again.');
    } finally {
      hideLoading();
    }
  });
});

// Sample data generator function with backwash simulation (fallback)
function generateSampleData(type, params) {
  if (type === 'pressure') {
    let data = [];
    let backwashPoints = [];
    let currentValue = 4 + (params.turb * 2);
    let trend = 0.3 + (params.turb * 0.2);
    
    // Apply fouling status effect
    const foulingStatus = 'clean'; // Default for fallback
    const foulingFactor = FOULING_FACTORS[foulingStatus];
    trend *= foulingFactor;
    
    // Temperature effect on trend
    trend *= (params.temp / 25.0);
    
    let lastBackwashStep = -1;
    
    for (let i = 0; i < 20; i++) {
      data.push(currentValue);
      
      if (currentValue >= PRESSURE_THRESHOLD && (i - lastBackwashStep) > 4) {
        const backwashParams = calculateBackwashParams(currentValue, params);
        
        backwashPoints.push({
          time_step: i,
          pressure: currentValue,
          intensity: backwashParams.intensity,
          duration: backwashParams.duration,
          reason: 'pressure_threshold_exceeded'
        });
        
        lastBackwashStep = i;
        currentValue = currentValue * (1 - PRESSURE_DROP_FACTOR);
        
        const intensityFactor = backwashParams.intensity / 10;
        const durationFactor = backwashParams.duration / 300;
        const effectivenessFactor = (intensityFactor + durationFactor) / 2;
        
        trend *= (0.9 - (effectivenessFactor * 0.2));
        
        if (effectivenessFactor > 1.2) {
          currentValue *= 0.95;
        }
      }
      
      currentValue += trend + (Math.random() * 0.2);
    }
    
    return { data, backwashPoints };
  }
}

// Calculate backwash parameters (fallback)
function calculateBackwashParams(pressure, params) {
  const foulingStatus = 'clean';
  const foulingFactor = FOULING_FACTORS[foulingStatus];
  
  let baseIntensity = (pressure - PRESSURE_THRESHOLD) * 1.5 * foulingFactor;
  
  const phFactor = Math.abs(params.ph - 7.0) * 0.1 + 1;
  const tempFactor = (params.temp / 25.0);
  const turbFactor = (params.turb / 0.5) * 0.2 + 0.8;
  
  const intensity = baseIntensity * phFactor * tempFactor * turbFactor;
  const duration = BACKWASH_DURATIONS[Math.floor(Math.random() * BACKWASH_DURATIONS.length)];
  
  return {
    intensity: Math.round(intensity * 10) / 10,
    duration: duration
  };
}

