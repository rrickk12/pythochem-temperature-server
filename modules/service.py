# modules/service.py

import logging
from db_ops.db_manager import DatabaseManager
from modules.reader import DataReader
from modules.report import ReportGenerator

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SensorService:
    """
    Service layer to interact with sensor data.
    This abstracts underlying database operations and report generation.
    """
    def __init__(self, db_url='sqlite:///ble_data.db'):
        self.db_manager = DatabaseManager(db_url)
        self.data_reader = DataReader(self.db_manager)
        self.report_generator = ReportGenerator(self.data_reader)

    def get_all_sensors(self):
        sensors = self.db_manager.get_all_sensors()
        logger.debug("Service: Retrieved sensors: %s", sensors)
        return sensors

    def get_sensor_report(self, mac, start_timestamp, end_timestamp):
        report = self.report_generator.generate_sensor_report(mac, start_timestamp, end_timestamp)
        logger.debug("Service: Generated report for sensor %s", mac)
        return report

    def update_sensor_alert_policy(self, mac, temp_min=None, temp_max=None, humidity_min=None, humidity_max=None):
        self.db_manager.set_alert_policy(mac, temp_min, temp_max, humidity_min, humidity_max)
        logger.debug("Service: Updated alert policy for sensor %s", mac)
        return {"status": "Alert policy updated", "mac": mac}

    def update_sensor_schedule_policy(self, mac, delta_time):
        self.db_manager.set_schedule_policy(mac, delta_time)
        logger.debug("Service: Updated schedule policy for sensor %s", mac)
        return {"status": "Schedule policy updated", "mac": mac}

# Create a singleton instance for use in other modules.
sensor_service = SensorService()
