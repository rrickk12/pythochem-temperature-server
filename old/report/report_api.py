from flask import Blueprint, request, jsonify
from db_ops.db_handler import DatabaseManager
from modules.reader import DataReader
from modules.report import ReportGenerator

# Create a Flask blueprint with URL prefix '/report'
report_bp = Blueprint('report', __name__, url_prefix='/report')

# Create instances of DatabaseManager, DataReader, and ReportGenerator.
# These instances connect to your real database (e.g., SQLite) and use real data.
db_manager = DatabaseManager()  # Ensure this DB is populated with sensor readings
data_reader = DataReader(db_manager)
report_generator = ReportGenerator(data_reader)

@report_bp.route('/', methods=['GET'])
def index():
    """
    @description:
        Default endpoint for the Report dashboard.
    @output:
        JSON response with a welcome message.
    """
    return jsonify({"message": "Report dashboard home"}), 200

@report_bp.route('/sensor', methods=['GET'])
def get_sensor_report():
    """
    @description:
        Endpoint to retrieve sensor data reports for the visualizer.
    @parameters:
        GET query parameters: 
          - mac: Sensor MAC address.
          - start_timestamp: Start of the interval (ISO format).
          - end_timestamp: End of the interval (ISO format).
    @output:
        JSON response containing sensor report data, generated from real database entries.
    """
    mac = request.args.get('mac')
    start = request.args.get('start_timestamp')
    end = request.args.get('end_timestamp')
    
    # Check if all required query parameters are present
    if not mac or not start or not end:
        return jsonify({"error": "Missing required parameters: mac, start_timestamp, end_timestamp"}), 400

    # Generate the sensor report using ReportGenerator.
    # This will perform a real query to your database to retrieve readings for the sensor,
    # compute statistics, and return a report.
    report = report_generator.generate_sensor_report(mac, start, end)

    # If report is empty because of no data, consider returning an appropriate message.
    if not report["raw_data"]:
        return jsonify({"warning": "No sensor readings found for the specified period.", "statistics": report["statistics"]}), 200

    return jsonify(report), 200
