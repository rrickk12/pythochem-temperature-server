import logging
from flask import Blueprint, request, jsonify
from db_ops.db_manager import DatabaseManager
from modules.reader import DataReader
from modules.report import ReportGenerator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

report_bp = Blueprint('report', __name__, url_prefix='/report')

db_manager      = DatabaseManager()
data_reader     = DataReader(db_manager)
report_generator = ReportGenerator(data_reader)

@report_bp.route('/', methods=['GET'])
def index():
    """GET /report/ — home do dashboard de relatórios (JSON)."""
    return jsonify({"message": "Report dashboard home"}), 200

@report_bp.route('/sensor', methods=['GET'])
def get_sensor_report():
    """
    GET /report/sensor?mac=...&start_timestamp=...&end_timestamp=...
    — retorna estatísticas e leituras.
    """
    mac   = request.args.get('mac')
    start = request.args.get('start_timestamp')
    end   = request.args.get('end_timestamp')

    if not mac or not start or not end:
        return jsonify({
            "error": "Missing parameters: mac, start_timestamp, end_timestamp"
        }), 400

    report = report_generator.generate_sensor_report(mac, start, end)
    if not report.get("raw_data"):
        return jsonify({
            "warning": "No data in period",
            "statistics": report.get("statistics", {})
        }), 200

    return jsonify(report), 200
