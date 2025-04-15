# blueprints/report.py

import logging
from flask import Blueprint, request, jsonify
from db_ops.db_manager import DatabaseManager
from modules.reader import DataReader
from modules.report import ReportGenerator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

report_bp = Blueprint('report', __name__, url_prefix='/report')

# Instantiate dependencies.
db_manager = DatabaseManager()
data_reader = DataReader(db_manager)
report_generator = ReportGenerator(data_reader)

@report_bp.route('/', methods=['GET'])
def index():
    """
    Default endpoint for the Report dashboard.
    """
    return jsonify({"message": "Report dashboard home"}), 200

@report_bp.route('/sensor', methods=['GET'])
def get_sensor_report():
    """
    Retrieves sensor report data.
    Query parameters:
      - mac: Sensor MAC address.
      - start_timestamp: Start time (ISO format).
      - end_timestamp: End time (ISO format).
    """
    mac = request.args.get('mac')
    start = request.args.get('start_timestamp')
    end = request.args.get('end_timestamp')
    
    if not mac or not start or not end:
        return jsonify({"error": "Missing required parameters: mac, start_timestamp, end_timestamp"}), 400

    report = report_generator.generate_sensor_report(mac, start, end)
    if not report["raw_data"]:
        return jsonify({
            "warning": "No sensor readings found for the specified period.",
            "statistics": report["statistics"]
        }), 200

    return jsonify(report), 200
