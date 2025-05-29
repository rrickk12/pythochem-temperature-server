# app.py

import logging
from flask import Flask
from db_ops.db_manager import DatabaseManager, backfill_clean_reads
from scheduler.scheduler import SchedulerManager

# Blueprints
from blueprints.listener  import listener_bp    # '/api/data'
from blueprints.api       import api_bp         # '/api/sensors/...'
from blueprints.report    import report_bp      # '/report/...'
from blueprints.dashboard import dashboard_bp   # '/', '/sensor/<mac>', '/relatorios'

# Configura o logging global
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("sensor_dashboard_app")

def create_app():
    """
    Cria e configura a aplicação Flask:
      - Registra todos os blueprints
      - Inicia o SchedulerManager em background
    """
    app = Flask(__name__)
    # Para uso do {% do %} no Jinja (caso algum template use)
    app.jinja_env.add_extension('jinja2.ext.do')
    
    # Registrar blueprints
    app.register_blueprint(listener_bp)    # '/api/data'
    app.register_blueprint(api_bp)         # '/api/sensors/...'
    app.register_blueprint(report_bp)      # '/report/...'
    app.register_blueprint(dashboard_bp)   # '/', '/sensor/<mac>', '/relatorios'

    # Iniciar tarefas agendadas (background)
    # backfill_clean_reads()
    scheduler = SchedulerManager(DatabaseManager(), check_interval=60)
    scheduler.start()

    logger.info("Flask app inicializado: blueprints registrados e scheduler rodando.")
    return app

if __name__ == "__main__":
    app = create_app()
    # Executa o servidor na porta 5009, acessível externamente
    app.run(host='0.0.0.0', port=5009, debug=True)
