"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("sensor.js loaded.");

    // Utility to export sensor data from a given MAC address.
    const exportSensorData = (mac) => {
        fetch(`/view/export_sensor?mac=${encodeURIComponent(mac)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                alert("Export Successful: " + JSON.stringify(data));
                // Optionally trigger a file download if data.download_url exists.
            })
            .catch(error => {
                console.error("Error exporting sensor data:", error);
                alert("Error exporting sensor data.");
            });
    };

    // Attach export behavior.
    document.querySelectorAll('.export-sensor').forEach(button => {
        button.addEventListener('click', event => {
            event.preventDefault();
            const mac = button.getAttribute('data-mac');
            exportSensorData(mac);
        });
    });

    // Utility to open a modal and pre-populate its hidden field with the sensor MAC.
    const openModalForSensor = (modalId, mac) => {
        const modalEl = document.getElementById(modalId);
        if (modalEl) {
            const macInput = modalEl.querySelector('input[name="mac"]');
            if (macInput) {
                macInput.value = mac;
            }
            const modal = new bootstrap.Modal(modalEl);
            modal.show();
        } else {
            console.error(`Modal with id ${modalId} not found!`);
        }
    };

    // Attach event listeners for the alarm modal.
    document.querySelectorAll('.edit-alarm').forEach(button => {
        button.addEventListener('click', event => {
            event.preventDefault();
            const mac = button.getAttribute('data-mac');
            openModalForSensor('alarmModal', mac);
        });
    });

    // Attach event listeners for the schedule modal.
    document.querySelectorAll('.edit-schedule').forEach(button => {
        button.addEventListener('click', event => {
            event.preventDefault();
            const mac = button.getAttribute('data-mac');
            openModalForSensor('scheduleModal', mac);
        });
    });
});
