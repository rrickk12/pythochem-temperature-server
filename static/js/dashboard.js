"use strict";

document.addEventListener("DOMContentLoaded", () => {
  initInlineEditing();
  initExportPrompts();
  initAlarmForms();
  initSchedulerForms();
  renderAllSensorCharts();
});

// 1. Edição inline do nome do sensor
function initInlineEditing() {
  document.body.addEventListener("click", e => {
    const span = e.target.closest(".editable");
    if (!span) return;
    const mac = span.dataset.mac;
    const oldName = span.textContent.trim() || "Unnamed Sensor";
    const input = document.createElement("input");
    input.type = "text";
    input.value = oldName;
    input.className = "form-control form-control-sm";
    span.replaceWith(input);
    input.focus();

    const commit = () => {
      const newName = input.value.trim() || oldName;
      fetch(`/api/sensors/${encodeURIComponent(mac)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName })
      })
        .then(res => res.ok ? replaceInput(input, mac, newName) : replaceInput(input, mac, oldName))
        .catch(() => replaceInput(input, mac, oldName));
    };

    input.addEventListener("blur", commit);
    input.addEventListener("keydown", ev => {
      if (ev.key === "Enter") { ev.preventDefault(); commit(); }
      if (ev.key === "Escape") replaceInput(input, mac, oldName);
    });
  });
}

function replaceInput(input, mac, text) {
  const span = document.createElement("span");
  span.className = "editable";
  span.dataset.mac = mac;
  span.textContent = text;
  input.replaceWith(span);
}

// 2. Exportação rápida por sensor (prompt → endpoint)
function initExportPrompts() {
  const exportMac = document.getElementById("export-mac");
  const exportFrom = document.getElementById("export-from");
  const exportTo = document.getElementById("export-to");
  const exportInterval = document.getElementById("export-interval");
  const exportForm = document.getElementById("exportForm");
  const exportModal = document.getElementById("exportModal");

  if (!exportMac || !exportFrom || !exportTo || !exportInterval || !exportForm || !exportModal) {
    console.warn("Export modal elements missing in DOM; skipping export prompt setup.");
    return;
  }

  document.querySelectorAll(".export-sensor").forEach(btn => {
    btn.addEventListener("click", () => {
      exportMac.value = btn.dataset.mac;
      exportFrom.value = "";
      exportTo.value = "";
      exportInterval.value = "4";
      const modal = new bootstrap.Modal(exportModal);
      modal.show();
    });
  });

  exportForm.addEventListener("submit", function(e) {
    e.preventDefault();
    const mac = exportMac.value;
    const from = exportFrom.value;
    const to   = exportTo.value;
    const hrs  = exportInterval.value;
    if (!mac || !from || !to || !hrs) return;
    bootstrap.Modal.getInstance(exportModal).hide();
    // Troque '/export' por '/export_excel'
    window.location.href = `/api/sensors/${encodeURIComponent(mac)}/export_excel`
      + `?from=${from}&to=${to}&interval=${hrs}`;
  });

}
// 3. Alarme inline por sensor (form .alarm-form)
function initAlarmForms() {
  document.querySelectorAll('.alarm-form').forEach(form => {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const mac = form.dataset.mac;
      const temp_min = parseFloat(form.temp_min.value);
      const temp_max = parseFloat(form.temp_max.value);
      const humidity_min   = parseFloat(form.humidity_min.value);
      const humidity_max= parseFloat(form.humidity_max.value);
      const body = { temp_min, temp_max, humidity_min, humidity_max  };

      const resp = await fetch(`/api/sensors/${encodeURIComponent(mac)}/alarms`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      if (resp.ok) {
        showFeedback(form, "Limites de alarme salvos! ✔️", true);
      } else {
        showFeedback(form, "Erro ao salvar limites!", false);
      }
    });
  });
}

// 4. Agendamento inline por sensor (form .scheduler-form)
function initSchedulerForms() {
  document.querySelectorAll('.scheduler-form').forEach(form => {
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const mac = form.dataset.mac;
      const delta_time = parseFloat(form.delta_time.value);
      if (!delta_time) return showFeedback(form, "Preencha o intervalo!", false);

      const resp = await fetch(`/api/sensors/${encodeURIComponent(mac)}/schedules`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ delta_time })
      });

      if (resp.ok) {
        showFeedback(form, "Agendamento salvo! ✔️", true);
      } else {
        showFeedback(form, "Erro ao salvar agendamento!", false);
      }
    });
  });
}

// Feedback inline (simples, pode trocar por toast)
function showFeedback(form, msg, ok) {
  let feedback = form.querySelector(".form-feedback");
  if (!feedback) {
    feedback = document.createElement("div");
    feedback.className = "form-feedback";
    form.appendChild(feedback);
  }
  feedback.textContent = msg;
  feedback.style.color = ok ? "#28a745" : "#dc3545";
  setTimeout(() => feedback.textContent = "", 2400);
}

// 5. Renderização dos mini-charts (Chart.js)
function renderAllSensorCharts() {
  if (!window.sensorChartData) return;
  Object.entries(window.sensorChartData).forEach(([mac, data]) =>
    renderSensorChart(mac, data)
  );
}

function renderSensorChart(mac, data) {
  const canvas = document.getElementById(`chart-${mac}`);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const card = canvas.closest(".sensor-card");

  const tmin = parseFloat(card.dataset.tempMin) || null;
  const tmax = parseFloat(card.dataset.tempMax) || null;
  const hmin = parseFloat(card.dataset.humMin) || null;
  const hmax = parseFloat(card.dataset.humMax) || null;

  // Labels (horário curto)
  const labels = data.map(r => r.timestamp?.slice(11, 16) || "");

  // Dados
  const temps = data.map(r => r.avg_temp ?? r.temperature ?? null);
  const hums = data.map(r => r.avg_hum ?? r.humidity ?? null);

  // Cores dos pontos (fora dos limites)
  const tempColors = temps.map(v =>
    (tmin !== null && tmax !== null && (v < tmin || v > tmax))
      ? "rgba(220,53,69,0.9)"
      : "rgba(0,123,255,0.9)"
  );
  const humColors = hums.map(v =>
    (hmin !== null && hmax !== null && (v < hmin || v > hmax))
      ? "rgba(255,111,0,0.8)"
      : "rgba(40,167,69,0.9)"
  );

  // Gráfico
  new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Temp (°C)",
          data: temps,
          borderColor: "rgba(0,123,255,1)",
          backgroundColor: "rgba(0,123,255,0.07)",
          pointBackgroundColor: tempColors,
          pointRadius: ctx => ctx.dataIndex === temps.length-1 ? 6 : 3,
          pointBorderWidth: ctx => ctx.dataIndex === temps.length-1 ? 2 : 1,
          tension: 0.3,
          yAxisID: "y-temp",
          fill: false
        },
        {
          label: "Hum (%)",
          data: hums,
          borderColor: "rgba(40,167,69,1)",
          backgroundColor: "rgba(40,167,69,0.07)",
          pointBackgroundColor: humColors,
          pointRadius: ctx => ctx.dataIndex === hums.length-1 ? 6 : 3,
          pointBorderWidth: ctx => ctx.dataIndex === hums.length-1 ? 2 : 1,
          tension: 0.3,
          yAxisID: "y-hum",
          fill: false
        },
        // Linhas de limite de temperatura
        ...(tmin !== null ? [makeLine("Temp Min", data.length, tmin, [6, 6], "#ffc107")] : []),
        ...(tmax !== null ? [makeLine("Temp Max", data.length, tmax, [6, 6], "#ffc107")] : []),
        ...(hmin !== null ? [makeLine("Hum Min", data.length, hmin, [4, 4], "#17a2b8")] : []),
        ...(hmax !== null ? [makeLine("Hum Max", data.length, hmax, [4, 4], "#17a2b8")] : []),
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      elements: {
        line: { borderWidth: 2 },
      },
      scales: {
        x: { display: false },
        "y-temp": {
          display: true,
          position: 'left',
          grid: { display: false },
          ticks: { color: "#0d6efd", font: { size: 11 } }
        },
        "y-hum": {
          display: true,
          position: 'right',
          grid: { display: false },
          ticks: { color: "#28a745", font: { size: 11 } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          callbacks: {
            label: ctx => `${ctx.dataset.label}: ${ctx.raw}`
          }
        },
        annotation: {
          // Para colocar valores grandes ou último valor: pode usar plugin extra ou custom
        }
      }
    }
  });
}

function makeLine(label, n, value, dash, color) {
  return {
    label,
    data: new Array(n).fill(value),
    borderColor: color,
    borderDash: dash,
    pointRadius: 0,
    borderWidth: 1.4,
    fill: false,
    yAxisID: label.startsWith("Hum") ? "y-hum" : "y-temp",
  };
}


  document.getElementById("exportAllForm").addEventListener("submit", function(e) {
    e.preventDefault();
    const from = document.getElementById("export-all-from").value;
    const to = document.getElementById("export-all-to").value;
    const interval = document.getElementById("export-all-interval").value;
    if (!from || !to || !interval) return;

    // Fecha o modal
    bootstrap.Modal.getInstance(document.getElementById("exportAllModal")).hide();

    // Troque '/export_all' por '/export_all_excel'
    window.location.href =
      `/api/sensors/export_all_excel?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}&interval=${interval}`;
  });