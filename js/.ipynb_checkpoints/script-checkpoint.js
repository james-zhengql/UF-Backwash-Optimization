// Initialize charts
let pressureChart = null;

// Constants for pressure threshold
const PRESSURE_THRESHOLD = 7.0; // 降低阈值使backwash更容易触发
const PRESSURE_DROP_FACTOR = 0.5; // 增加压力下降幅度到50%

// 可选的反洗时间（秒）
const BACKWASH_DURATIONS = [140, 220, 360, 460];

// 计算反洗强度和时间的函数
function calculateBackwashParams(pressure, params) {
    // 基于压力值和水质参数计算反洗强度和时间
    let intensity;
    
    // 基础反洗强度基于压力值
    let baseIntensity = (pressure - PRESSURE_THRESHOLD) * 1.5;
    
    // 根据水质参数调整反洗强度
    const phFactor = Math.abs(params.ph - 7.0) * 0.1 + 1; // pH偏离7.0越多，强度越大
    const tempFactor = (params.temp / 25.0); // 温度越高，强度略微增加
    const turbFactor = (params.turb / 0.5) * 0.2 + 0.8; // 浊度越高，强度越大
    
    intensity = baseIntensity * phFactor * tempFactor * turbFactor;
    
    // 随机选择一个反洗时间
    const duration = BACKWASH_DURATIONS[Math.floor(Math.random() * BACKWASH_DURATIONS.length)];
    
    return {
        intensity: Math.round(intensity * 10) / 10, // 保留一位小数
        duration: duration
    };
}

// Sample data generator function with backwash simulation
function generateSampleData(type, params) {
    if (type === 'pressure') {
        let data = [];
        let backwashPoints = [];
        let currentValue = 5;
        let trend = 0.4;
        
        // 根据水质参数调整初始值和趋势
        currentValue = 4 + (params.turb * 2); // 浊度越高，初始压力越大
        trend = 0.3 + (params.turb * 0.2); // 浊度越高，压力上升越快
        
        // 温度对趋势有轻微影响
        trend *= (params.temp / 25.0);
        
        let lastBackwashStep = -1;  // 记录上次backwash的时间步骤
        
        // 生成数据
        for (let i = 0; i < 20; i++) {
            // 保存当前值
            data.push(currentValue);
            
            // 检查当前值是否达到阈值，并且与上次backwash间隔至少3个步骤
            if (currentValue >= PRESSURE_THRESHOLD && (i - lastBackwashStep) > 4) {
                console.log(`Backwash triggered at step ${i}, pressure: ${currentValue}`);
                
                // 计算反洗参数
                const backwashParams = calculateBackwashParams(currentValue, params);
                
                // 记录backwash点
                backwashPoints.push({
                    timeStep: i,  // 使用当前步骤
                    pressure: currentValue,
                    intensity: backwashParams.intensity,
                    duration: backwashParams.duration
                });
                
                lastBackwashStep = i;  // 更新上次backwash时间
                
                // 触发backwash，压力下降
                currentValue = currentValue * (1 - PRESSURE_DROP_FACTOR);
                
                // 根据反洗强度和时间调整趋势
                const intensityFactor = backwashParams.intensity / 10; // 假设10是基准强度
                const durationFactor = backwashParams.duration / 300; // 假设300秒是基准时间
                const effectivenessFactor = (intensityFactor + durationFactor) / 2;
                
                // 减小上升趋势，效果越好减小越多
                trend *= (0.9 - (effectivenessFactor * 0.2));
                
                // 如果反洗效果特别好（高强度和长时间），额外降低压力
                if (effectivenessFactor > 1.2) {
                    currentValue *= 0.95;
                }
            }
            
            // 计算下一个值
            currentValue += trend + (Math.random() * 0.2);
        }
        
        console.log('Pressure data:', data);
        console.log('Backwash points:', backwashPoints);
        return { data, backwashPoints };
    }
}

// Create a chart
function createChart(ctx, label, data, type = 'default') {
    console.log('Creating chart:', label, 'Context:', ctx);
    if (!ctx) {
        console.error('Canvas context is null for', label);
        return null;
    }
    
    // Create labels for time steps 1-20
    const labels = Array.from({length: 20}, (_, i) => i + 1);
    
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
                        // 检查是否是backwash点
                        const isBackwashPoint = data.backwashPoints.some(point => 
                            point.timeStep === context.dataIndex
                        );
                        return isBackwashPoint ? 8 : 5;
                    }
                    return 5;
                },
                pointHoverRadius: 8,
                pointBackgroundColor: (context) => {
                    if (type === 'pressure' && data.backwashPoints) {
                        // 检查是否是backwash点
                        const isBackwashPoint = data.backwashPoints.some(point => 
                            point.timeStep === context.dataIndex
                        );
                        return isBackwashPoint ? 'rgb(255, 99, 132)' : 'rgb(75, 192, 192)';
                    }
                    return 'rgb(75, 192, 192)';
                },
                pointBorderColor: (context) => {
                    if (type === 'pressure' && data.backwashPoints) {
                        // 检查是否是backwash点
                        const isBackwashPoint = data.backwashPoints.some(point => 
                            point.timeStep === context.dataIndex
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
                    max: 15, // 增加y轴最大值以容纳标签
                    grid: {
                        drawBorder: true,
                        color: function(context) {
                            if (context.tick.value > 10) {
                                return 'rgba(0,0,0,0)'; // 10以上的网格线透明
                            }
                            return 'rgba(0,0,0,0.1)';
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            if (value > 10) {
                                return ''; // 不显示10以上的刻度值
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
                                // 检查是否是backwash点
                                const backwashPoint = data.backwashPoints.find(point => 
                                    point.timeStep === context.dataIndex
                                );
                                if (backwashPoint) {
                                    return [
                                        `Pressure: ${value} PSIG`,
                                        `Backwash Intensity: ${backwashPoint.intensity} W`,
                                        `Backwash Duration: ${backwashPoint.duration} s`
                                    ];
                                }
                                return `Pressure: ${value} PSIG`;
                            }
                            return `Value: ${value}`;
                        }
                    }
                }
            }
        }
    };

    // Add backwash point annotations
    if (type === 'pressure' && data.backwashPoints.length > 0) {
        chartConfig.options.plugins.annotation = {
            annotations: data.backwashPoints.reduce((acc, point, index) => {
                // 计算标签位置，确保在图表范围内
                const baseYValue = 13; // 在y轴上方的固定位置
                const xOffset = 0; // 水平偏移量
                
                acc[`backwashBox${index}`] = {
                    type: 'label',
                    xValue: point.timeStep,
                    yValue: baseYValue,
                    backgroundColor: 'rgba(255, 99, 132, 0.9)',
                    content: [
                        'Backwash Point',
                        `Intensity: ${point.intensity} W`,
                        `Duration: ${point.duration} s`
                    ],
                    font: {
                        size: 11,
                        weight: 'bold'
                    },
                    color: 'white',
                    padding: {
                        top: 4,
                        bottom: 4,
                        left: 6,
                        right: 6
                    },
                    borderRadius: 4,
                    xAdjust: xOffset,
                    position: 'center',
                    display: true
                };

                // 添加连接线
                acc[`backwashLine${index}`] = {
                    type: 'line',
                    xMin: point.timeStep,
                    xMax: point.timeStep,
                    yMin: point.pressure,
                    yMax: baseYValue - 0.5,
                    borderColor: 'rgba(255, 99, 132, 0.5)',
                    borderWidth: 1,
                    borderDash: [2, 2]
                };
                
                return acc;
            }, {})
        };
    }

    return new Chart(ctx, chartConfig);
}

// Update or create charts
function updateCharts() {  // 移除 mode 参数
    console.log('Updating charts...');
    
    const chartSection = document.getElementById('chart-section');
    console.log('Chart section display style:', chartSection.style.display);
    
    // Get canvas elements
    const pressureCtx = document.getElementById('pressureChart');
    
    // Get input values
    const params = {
        ph: parseFloat(document.getElementById('ph-input').value),
        temp: parseFloat(document.getElementById('temp-input').value),
        turb: parseFloat(document.getElementById('turb-input').value)
    };
    
    console.log('Canvas elements found:', {
        pressureChart: !!pressureCtx
    });

    if (!pressureCtx) {
        console.error('Pressure canvas element not found');
        return;
    }

    // Destroy existing chart if it exists
    if (pressureChart) {
        console.log('Destroying existing pressure chart');
        pressureChart.destroy();
    }

    // Create new chart
    console.log('Creating new chart...');
    pressureChart = createChart(pressureCtx.getContext('2d'), 'Pressure Drop', generateSampleData('pressure', params), 'pressure');
    
    console.log('Chart created:', {
        pressureChart: !!pressureChart
    });
}

// Handle forecast button click
function handleForecastClick() {
    console.log('Forecast button clicked');

    // Show the chart section
    const chartSection = document.getElementById('chart-section');
    chartSection.style.display = 'block';
    
    // Add a small delay to allow the display change to take effect
    setTimeout(() => {
        chartSection.classList.add('show');
        
        // Update charts with new data
        console.log('Calling updateCharts after delay');
        updateCharts();  // 移除 mode 参数
        
        // Scroll to the charts section
        chartSection.scrollIntoView({ behavior: 'smooth' });
    }, 50);
}

// Initialize carousel behavior
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');

    // Add click event listener to forecast button
    const forecastBtn = document.getElementById('forecast-btn');
    if (forecastBtn) {
        console.log('Forecast button found, adding click listener');
        forecastBtn.addEventListener('click', handleForecastClick);
    } else {
        console.error('Forecast button not found!');
    }
});

