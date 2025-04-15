// static/js/chart.js

document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('sensorChart');
    if (!canvas) {
        console.warn("No sensorChart canvas found.");
        return;
    }
    const ctx = canvas.getContext('2d');

    // Retrieve sensor readings passed from the backend.
    // This can be a global variable (e.g., passed via a template) or set in the HTML.
    const readings = window.sensorReadings || [];

    // Sort readings by timestamp to ensure the chart displays chronologically.
    readings.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    const labels = readings.map(r => r.timestamp);
    // Use the average temperature if available, otherwise fallback to raw.
    const temperatureData = readings.map(r => r.avg_temp || r.temperature);
    // Use the average humidity if available, otherwise fallback to raw.
    const humidityData = readings.map(r => r.avg_hum || r.humidity);

    // Render the chart using Chart.js.
    const sensorChart = new Chart(ctx, {
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
