from flask import Flask, render_template
import logging

# Import blueprints and service layer from refactored modules.
from blueprints.listener import listener_bp
from blueprints.report import report_bp       # Report API endpoints
from blueprints.view import view_bp            # Dashboard/management endpoints
from modules.service import sensor_service

# Set up application-wide logging.
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """
    Factory function that creates, configures, and returns the Flask application.
    It registers all blueprints and exposes main pages.
    """
    app = Flask(__name__)

    # Register API endpoints using blueprints.
    app.register_blueprint(listener_bp, url_prefix='/api')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(view_bp, url_prefix='/view')

    @app.route("/")
    def index():
        """
        Renders the dashboard homepage.
        This page displays the list of sensors currently in the system.
        """
        logger.info("Rendering dashboard page.")
        sensors = sensor_service.get_all_sensors()
        return render_template("index.html", sensors=sensors)

    @app.route("/sensor/<mac>")
    def sensor_detail(mac):
        """
        Renders a detailed page for a single sensor.
        It retrieves sensor metadata along with its latest readings.
        """
        from db_ops.db_manager import DatabaseManager
        import json
        db_manager = DatabaseManager()
        sensor = db_manager.get_sensor(mac)
        if not sensor:
            return "Sensor not found", 404

        # Retrieve latest clean readings if available, else raw readings.
        if hasattr(db_manager, 'get_latest_clean_reads'):
            readings = db_manager.get_latest_clean_reads(mac, limit=50)
        else:
            readings = db_manager.get_latest_raw_reads(mac, limit=50)

        # Format the readings into dictionaries.
        formatted_readings = [{
            'timestamp': r.timestamp,
            'temperature': getattr(r, 'temperature', None),
            'humidity': getattr(r, 'humidity', None),
            'avg_temp': getattr(r, 'avg_temp', None),
            'avg_hum': getattr(r, 'avg_hum', None)
        } for r in readings]

        # Serialize readings to JSON so they can be injected into the template.
        readings_json = json.dumps(formatted_readings)

        return render_template("sensor_detail.html", sensor=sensor, raw_data=formatted_readings, readings_json=readings_json)

    return app

if __name__ == "__main__":
    app = create_app()
    # Run the application on host 0.0.0.0 (accessible externally) with port 5009.
    app.run(host='0.0.0.0', port=5009, debug=True)
