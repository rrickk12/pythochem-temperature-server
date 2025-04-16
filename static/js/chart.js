"use strict";

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('sensorChart');
    if (!canvas) {
        console.warn("No sensorChart canvas found.");
        return;
    }
    const ctx = canvas.getContext('2d');

    // Ensure that sensor readings are provided.
    const readings = window.sensorReadings || [];
    if (!readings.length) {
        console.warn("No sensor readings available to render chart.");
        return;
    }

    // Sort readings chronologically.
    readings.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    const labels = readings.map(r => r.timestamp);
    const temperatureData = readings.map(r => r.avg_temp ?? r.temperature);
    const humidityData = readings.map(r => r.avg_hum ?? r.humidity);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temperatureData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.3
                },
                {
                    label: 'Humidity (%)',
                    data: humidityData,
                    borderColor: 'rgba(153, 102, 255, 1)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    display: true,
                    title: { display: true, text: 'Time' }
                },
                y: {
                    display: true,
                    title: { display: true, text: 'Value' }
                }
            },
            plugins: {
                legend: { display: true, position: 'bottom' }
            }
        }
    });
});
