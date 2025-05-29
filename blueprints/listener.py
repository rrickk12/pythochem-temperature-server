import logging
from flask import Blueprint, request, jsonify
from utils import parser
from utils.validators import validate_sensor_payload
from db_ops.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

listener_bp = Blueprint('listener', __name__, url_prefix='/api/data')
db_manager = DatabaseManager()

@listener_bp.route('/', methods=['POST'])
def receive_data():
    """
    Recebe payload JSON (objeto ou lista) com leituras brutas de sensores.
    Exemplo POST /api/data/ { … }
    """
    data = request.get_json()
    if not data:
        logger.warning("Nenhum dado recebido de %s", request.remote_addr)
        return jsonify({"error": "No data provided"}), 400

    try:
        structured = parser.parse_payload(data)
        # Se for um único objeto, valida antes de inserir
        if isinstance(structured, dict):
            valid, errors = validate_sensor_payload(structured)
            if not valid:
                return jsonify({"error": "Invalid payload", "details": errors}), 400

        count = 0
        if isinstance(structured, list):
            for rec in structured:
                db_manager.insert_raw_read(rec)
            count = len(structured)
        else:
            db_manager.insert_raw_read(structured)
            count = 1

        logger.info("Inseridos %d registro(s) de %s", count, request.remote_addr)
        return jsonify({"status": "success", "inserted": count}), 200

    except Exception as e:
        logger.exception("Erro ao processar dados de %s: %s", request.remote_addr, e)
        return jsonify({"error": str(e)}), 500
