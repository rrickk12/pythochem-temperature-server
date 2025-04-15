from flask import Blueprint, request, jsonify
from services.sensor_service import sensor_service
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

view_bp = Blueprint('view', __name__, url_prefix='/view')

@view_bp.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Manage dashboard home"}), 200

@view_bp.route('/reports/sensor', methods=['GET'])
def sensor_report():
    """
    Retrieve a sensor report.
    Query Parameters:
      - mac: Sensor MAC address.
      - start_timestamp: Start of the interval (ISO format).
      - end_timestamp: End of the interval (ISO format).
    """
    mac = request.args.get('mac')
    start = request.args.get('start_timestamp')
    end = request.args.get('end_timestamp')
    
    if not mac or not start or not end:
        logger.warning("Missing parameters in sensor report request")
        return jsonify({"error": "Missing parameters"}), 400

    report = sensor_service.get_sensor_report(mac, start, end)
    logger.info("Service: Generated report for sensor %s", mac)
    return jsonify(report), 200

@view_bp.route('/alarms', methods=['POST'])
def set_alarm():
    """
    Set or update alert policies (alarms) for a sensor.
    Expected JSON Payload: { "mac": ..., "temp_min": ..., "temp_max": ..., "humidity_min": ..., "humidity_max": ... }
    """
    data = request.get_json()
    if not data or "mac" not in data:
        logger.warning("Missing sensor MAC in alarm request")
        return jsonify({"error": "Missing sensor MAC"}), 400

    result = sensor_service.update_sensor_alert_policy(
        data["mac"],
        temp_min=data.get("temp_min"),
        temp_max=data.get("temp_max"),
        humidity_min=data.get("humidity_min"),
        humidity_max=data.get("humidity_max")
    )
    return jsonify(result), 200

@view_bp.route('/schedules', methods=['POST'])
def set_schedule():
    """
    Set or update schedule policies for a sensor.
    Expected JSON Payload: { "mac": ..., "delta_time": ... }
    """
    data = request.get_json()
    if not data or "mac" not in data or "delta_time" not in data:
        logger.warning("Missing required parameters in schedule request")
        return jsonify({"error": "Missing required parameters"}), 400

    result = sensor_service.update_sensor_schedule_policy(data["mac"], data["delta_time"])
    return jsonify(result), 200

@view_bp.route('/export_all', methods=['GET'])
def export_all():
    logger.info("Export all sensor data requested via service layer.")
    # Placeholder: implement export logic in your service if needed.
    exported_data = {"data": "Export all sensor data (placeholder)"}
    return jsonify(exported_data), 200

@view_bp.route('/update_sensor/<mac>', methods=['POST'])
def update_sensor(mac):
    data = request.form
    logger.info("Updating sensor %s with data: %s", mac, data)
    # Placeholder response
    return jsonify({"status": "Sensor updated", "mac": mac}), 200
