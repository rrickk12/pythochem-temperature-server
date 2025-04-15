# blueprints/listener.py

import logging
from flask import Blueprint, request, jsonify
from utils import parser  # Assume a parser module exists in your project
from utils.validators import validate_sensor_payload
from db_ops.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

listener_bp = Blueprint('listener', __name__)

# Create an instance of the DatabaseManager.
db_manager = DatabaseManager()

@listener_bp.route('/data', methods=['POST'])
def receive_data():
    """
    Processes incoming POST data from the BLE gateway.
    Expects a JSON payload containing sensor readings (a single object or list).
    """
    data = request.get_json()
    logger.debug("Received POST data: %s", data)
    
    if not data:
        logger.warning("No data provided in POST request from %s", request.remote_addr)
        return jsonify({"error": "No data provided"}), 400

    try:
        structured_data = parser.parse_payload(data)
        if isinstance(structured_data, dict):
            valid, errors = validate_sensor_payload(structured_data)
            if not valid:
                return jsonify({"error": "Invalid payload", "details": errors}), 400
        logger.debug("Structured data: %s", structured_data)
        
        inserted_count = 0
        if isinstance(structured_data, list):
            for reading in structured_data:
                db_manager.insert_raw_read(reading)
            inserted_count = len(structured_data)
        else:
            db_manager.insert_raw_read(structured_data)
            inserted_count = 1

        logger.info("Inserted %s record(s) from %s", inserted_count, request.remote_addr)
        return jsonify({"status": "success", "inserted": inserted_count}), 200
    except Exception as e:
        logger.exception("Error processing POST data from %s: %s", request.remote_addr, e)
        return jsonify({"error": str(e)}), 500
