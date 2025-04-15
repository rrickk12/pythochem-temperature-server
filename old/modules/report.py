# modules/report.py
import logging
from modules.reader import DataReader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ReportGenerator:
    """
    @description: Provides methods to generate and export sensor reports.
    """
    def __init__(self, data_reader: DataReader):
        self.data_reader = data_reader

    def generate_sensor_report(self, mac, start_timestamp, end_timestamp):
        """
        @description: Generates a summary report for a sensor over a specified interval.
        @output: Dictionary with aggregated statistics and sample raw data.
        """
        stats = self.data_reader.get_statistics(mac, start_timestamp, end_timestamp)
        raw_data = self.data_reader.get_raw_data(mac, limit=50)
        # Convert raw data objects to dicts if necessary.
        report = {
            "statistics": stats,
            "raw_data": [record.__dict__ for record in raw_data]
        }
        logger.debug("Generated report for sensor %s: %s", mac, report)
        return report

    def export_report_to_csv(self, report_data, filename):
        """
        @description: Exports report data to a CSV file.
        @output: None (writes CSV to disk).
        """
        import csv
        with open(filename, 'w', newline='') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=report_data.keys())
            writer.writeheader()
            writer.writerow(report_data)
        logger.debug("Exported report to CSV file: %s", filename)
