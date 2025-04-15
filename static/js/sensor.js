// static/js/sensor.js

document.addEventListener('DOMContentLoaded', function () {
    console.log("sensor.js loaded.");

    // Attach export behavior to all export buttons.
    const exportButtons = document.querySelectorAll('.export-sensor');
    exportButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const mac = button.getAttribute('data-mac');
            exportSensorData(mac);
        });
    });

    // Open the alarm modal to update thresholds.
    const alarmButtons = document.querySelectorAll('.edit-alarm');
    alarmButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const mac = button.getAttribute('data-mac');
            const alarmModalEl = document.getElementById('alarmModal');
            if (alarmModalEl) {
                // Pre-populate the hidden MAC field in the modal.
                const macInput = alarmModalEl.querySelector('input[name="mac"]');
                if (macInput) {
                    macInput.value = mac;
                }
                // Initialize and display the modal.
                const alarmModal = new bootstrap.Modal(alarmModalEl);
                alarmModal.show();
            } else {
                console.error("Alarm modal not found!");
            }
        });
    });

    // Open the schedule modal to update schedule policies.
    const scheduleButtons = document.querySelectorAll('.edit-schedule');
    scheduleButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const mac = button.getAttribute('data-mac');
            const scheduleModalEl = document.getElementById('scheduleModal');
            if (scheduleModalEl) {
                // Pre-populate the hidden MAC field in the modal.
                const macInput = scheduleModalEl.querySelector('input[name="mac"]');
                if (macInput) {
                    macInput.value = mac;
                }
                const scheduleModal = new bootstrap.Modal(scheduleModalEl);
                scheduleModal.show();
            } else {
                console.error("Schedule modal not found!");
            }
        });
    });

    /**
     * Exports sensor data by calling the designated endpoint.
     * @param {string} mac - The sensor MAC address.
     */
    function exportSensorData(mac) {
        fetch(`/view/export_sensor?mac=${encodeURIComponent(mac)}`)
            .then(response => response.json())
            .then(data => {
                alert("Export Successful: " + JSON.stringify(data));
                // Optionally, if a download URL is provided, trigger a file download.
            })
            .catch(error => {
                console.error("Error exporting sensor data:", error);
                alert("Error exporting sensor data.");
            });
    }
});
