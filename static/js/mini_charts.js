document.addEventListener('DOMContentLoaded', function () {
    if (!window.sensorChartData) return;
  
    Object.entries(window.sensorChartData).forEach(([mac, data]) => {
      const canvas = document.getElementById(`chart-${mac}`);
      if (!canvas) return;
  
      const ctx = canvas.getContext("2d");
  
      // Parse data
      const labels = data.map(r => r.timestamp.slice(11, 16));
      const temps = data.map(r => r.avg_temp ?? r.temperature ?? null);
      const hums = data.map(r => r.avg_hum ?? r.humidity ?? null);
  
      // Get min/max for overlay
      const tempMin = Math.min(...temps.filter(v => v !== null));
      const tempMax = Math.max(...temps.filter(v => v !== null));
      const humMin = Math.min(...hums.filter(v => v !== null));
      const humMax = Math.max(...hums.filter(v => v !== null));
      const overallMin = Math.min(tempMin, humMin);
      const overallMax = Math.max(tempMax, humMax);
  
      new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: "Temperature (°C)",
              data: temps,
              borderColor: 'rgba(255,99,132,1)',
              backgroundColor: 'rgba(255,99,132,0.1)',
              fill: false,
              tension: 0.3,
              pointRadius: 2
            },
            {
              label: "Humidity (%)",
              data: hums,
              borderColor: 'rgba(54, 162, 235, 1)',
              backgroundColor: 'rgba(54, 162, 235, 0.1)',
              fill: false,
              tension: 0.3,
              pointRadius: 2
            },
            {
              label: "Ideal Range",
              data: Array(data.length).fill(tempMin + 1), // Dummy line
              backgroundColor: 'rgba(0, 255, 0, 0.05)',
              borderWidth: 0,
              pointRadius: 0,
              type: 'line',
              fill: {
                target: {
                  value: tempMax - 1
                },
                above: 'rgba(0,255,0,0.05)',
                below: 'transparent'
              }
            }
          ]
        },
        options: {
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: context => `${context.dataset.label}: ${context.raw}`
              }
            }
          },
          scales: {
            x: {
              display: false
            },
            y: {
              display: false,
              min: overallMin - 2,
              max: overallMax + 2
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
    });
  });
  