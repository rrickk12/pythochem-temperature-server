import logging
from flask import Blueprint, request, jsonify
from utils import parser
from db_ops.db_handler import DatabaseManager

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a Flask blueprint for listener endpoints
listener_bp = Blueprint('listener', __name__)

# Create an instance of DatabaseManager (adjust instantiation as needed in your app)
db_manager = DatabaseManager()

@listener_bp.route('/data', methods=['POST'])
def receive_data():
    """
    @description
        Listens for POST requests from the BLE gateway, parses and processes the payload,
        and passes the extracted sensor data for further processing (e.g., database insertion).
    @parameters
        - POST /data with a JSON payload representing sensor readings from the gateway.
          The expected format is a JSON array of objects. For example:
          [{"timestamp": "2025-04-14T16:47:25.836Z", "type": "Gateway", "mac": "AC233FC02377", ...}, ...]
    @output
        - JSON response indicating success (with count of inserted records) or error message.
    """
    data = request.get_json()
    logger.debug("Received POST data: %s", data)
    
    if not data:
        logger.warning("No data provided in POST request from %s", request.remote_addr)
        return jsonify({"error": "No data provided"}), 400

    try:
        # Process the payload using the parser helper
        structured_data = parser.parse_payload(data)
        logger.debug("Structured data after parsing: %s", structured_data)
        
        inserted_count = 0
        # Check if the structured data is a list (multiple readings)
        if isinstance(structured_data, list):
            for reading in structured_data:
                db_manager.insert_raw_read(reading)
            inserted_count = len(structured_data)
        else:
            # Otherwise, assume it's a single reading
            db_manager.insert_raw_read(structured_data)
            inserted_count = 1

        logger.info("Successfully processed and inserted %s record(s) from %s", 
                    inserted_count, request.remote_addr)
        return jsonify({"status": "success", "inserted": inserted_count}), 200
    except Exception as e:
        logger.exception("Error processing POST data from %s: %s", request.remote_addr, e)
        return jsonify({"error": str(e)}), 500
