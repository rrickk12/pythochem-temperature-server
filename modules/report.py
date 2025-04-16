# modules/report.py

import logging
from modules.reader import DataReader

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ReportGenerator:
    """
    Generates sensor reports and provides CSV export functionality.
    """
    def __init__(self, data_reader: DataReader):
        self.data_reader = data_reader

    def generate_sensor_report(self, mac, start_timestamp, end_timestamp):
        """
        Generates a summary report for a sensor.
        Returns a dictionary containing aggregated statistics and sample raw data.
        """
        stats = self.data_reader.get_statistics(mac, start_timestamp, end_timestamp)
        raw_data = self.data_reader.get_raw_data(mac, limit=50)
        report = {
            "statistics": stats,
            "raw_data": [record.__dict__ for record in raw_data]
        }
        logger.debug("Generated report for sensor %s: %s", mac, report)
        return report

    def export_report_to_csv(self, report_data, filename):
        """
        Exports report data to a CSV file.
        """
        import csv
        with open(filename, 'w', newline='') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=report_data.keys())
            writer.writeheader()
            writer.writerow(report_data)
        logger.debug("Exported report to CSV file: %s", filename)
