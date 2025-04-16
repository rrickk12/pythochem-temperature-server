# modules/reader.py

import logging
from db_ops.db_manager import DatabaseManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DataReader:
    """
    Utility to read sensor data from the database and compute statistics.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_raw_data(self, mac, limit=100):
        """
        Retrieves the latest raw readings for a sensor.
        """
        data = self.db_manager.get_latest_raw_reads(mac, limit)
        logger.debug("Retrieved raw data for sensor %s: %s", mac, data)
        return data

    def get_statistics(self, mac, start_timestamp, end_timestamp):
        """
        Computes aggregated statistics for a sensor over a given interval.
        """
        stats = self.db_manager.compute_statistics(mac, start_timestamp, end_timestamp)
        logger.debug("Computed statistics for sensor %s: %s", mac, stats)
        return stats
