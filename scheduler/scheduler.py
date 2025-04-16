# scheduler/scheduler.py

import threading
import time
import datetime
import logging
from sqlalchemy import func, Float
from db_ops.db_manager import DatabaseManager
from db_ops.models import ReadRaw

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SchedulerManager:
    """
    Orchestrates scheduled operations such as data compression and alert checking.
    """
    def __init__(self, db_manager: DatabaseManager, check_interval=60):
        self.db_manager = db_manager
        self.check_interval = check_interval  # Interval in seconds.
        self.running = False
        logger.debug("SchedulerManager initialized with check interval %s seconds", check_interval)

    def start(self):
        """Starts the scheduler loop in a daemon thread."""
        self.running = True
        threading.Thread(target=self._run_loop, daemon=True).start()
        logger.info("Scheduler started.")

    def stop(self):
        """Stops the scheduler loop."""
        self.running = False
        logger.info("Scheduler stopped.")

    def _run_loop(self):
        while self.running:
            logger.debug("--- Scheduler Cycle Started ---")
            self.register_schedule_timestamps()
            self.clean_and_compress_reads()
            self.register_scheduled_reads()
            self.check_alerts()
            logger.debug("--- Scheduler Cycle Finished ---")
            time.sleep(self.check_interval)

    def register_schedule_timestamps(self):
        logger.debug("Registering schedule timestamps...")
        sensors = self.db_manager.get_all_sensors()
        now = datetime.datetime.utcnow()
        for sensor in sensors:
            schedule_policy = self.db_manager.get_schedule_policy(sensor.mac)
            if schedule_policy:
                if schedule_policy.last_update:
                    last_update = datetime.datetime.fromisoformat(schedule_policy.last_update)
                else:
                    last_update = now - datetime.timedelta(seconds=schedule_policy.delta_time + 1)
                if (now - last_update).total_seconds() >= schedule_policy.delta_time:
                    self.db_manager.update_schedule_policy_last_update(sensor.mac, now.isoformat())
                    logger.debug("Updated schedule timestamp for sensor %s", sensor.mac)

    def clean_and_compress_reads(self):
        logger.debug("Compressing raw reads into clean data...")
        sensors = self.db_manager.get_all_sensors()
        now = datetime.datetime.utcnow()
        minute_start = now.replace(second=0, microsecond=0).isoformat()
        for sensor in sensors:
            self.db_manager.compress_minute_reads(sensor.mac, minute_start)
            logger.debug("Compressed minute reads for sensor %s at %s", sensor.mac, minute_start)

    def register_scheduled_reads(self):
        logger.debug("Registering scheduled reads...")
        sensors = self.db_manager.get_all_sensors()
        now = datetime.datetime.utcnow()
        interval_start = now.replace(minute=0, second=0, microsecond=0).isoformat()
        interval_end = now.isoformat()
        for sensor in sensors:
            schedule_policy = self.db_manager.get_schedule_policy(sensor.mac)
            if schedule_policy:
                now_ts = now.timestamp()
                last_update = datetime.datetime.fromisoformat(schedule_policy.last_update) if schedule_policy.last_update else None
                elapsed = now_ts - (last_update.timestamp() if last_update else 0)
                if elapsed >= schedule_policy.delta_time:
                    self.db_manager.compress_schedule_reads(sensor.mac, interval_start, interval_end)
                    logger.debug("Registered scheduled read for sensor %s from %s to %s", sensor.mac, interval_start, interval_end)

    def check_alerts(self):
        logger.debug("Checking alerts for sensors...")
        sensors = self.db_manager.get_all_sensors()
        for sensor in sensors:
            alert_policy = self.db_manager.get_alert_policy(sensor.mac)
            if alert_policy:
                raw_reads = self.db_manager.get_latest_raw_reads(sensor.mac, limit=1)
                if raw_reads:
                    last_read = raw_reads[0]
                    alerts_triggered = []
                    if alert_policy.temp_max is not None and last_read.temperature is not None:
                        if last_read.temperature > alert_policy.temp_max:
                            alerts_triggered.append("temp_high")
                    if alert_policy.temp_min is not None and last_read.temperature is not None:
                        if last_read.temperature < alert_policy.temp_min:
                            alerts_triggered.append("temp_low")
                    if alert_policy.humidity_max is not None and last_read.humidity is not None:
                        if last_read.humidity > alert_policy.humidity_max:
                            alerts_triggered.append("humidity_high")
                    if alert_policy.humidity_min is not None and last_read.humidity is not None:
                        if last_read.humidity < alert_policy.humidity_min:
                            alerts_triggered.append("humidity_low")
                    for alert in alerts_triggered:
                        warning_data = {
                            "timestamp": last_read.timestamp,
                            "mac": sensor.mac,
                            "type": alert,
                            "message": f"{alert} alert triggered for sensor {sensor.mac}",
                            "read": False,
                            "posted": False
                        }
                        self.db_manager.insert_warning(warning_data)
                        logger.debug("Inserted warning for sensor %s: %s", sensor.mac, alert)

    def compute_statistics(self, mac, start_timestamp, end_timestamp):
        with self.db_manager.Session() as session:
            q = session.query(
                func.avg(func.cast(ReadRaw.temperature, Float)).label("avg_temp"),
                func.avg(func.cast(ReadRaw.humidity, Float)).label("avg_hum"),
                func.min(ReadRaw.temperature).label("min_temp"),
                func.max(ReadRaw.temperature).label("max_temp"),
                func.min(ReadRaw.humidity).label("min_hum"),
                func.max(ReadRaw.humidity, ).label("max_hum")
            ).filter(
                ReadRaw.mac == mac,
                ReadRaw.timestamp.between(start_timestamp, end_timestamp)
            ).first()
            stats = {
                "avg_temp": q.avg_temp,
                "avg_hum": q.avg_hum,
                "min_temp": q.min_temp,
                "max_temp": q.max_temp,
                "min_hum": q.min_hum,
                "max_hum": q.max_hum
            }
            logger.debug("Computed statistics for sensor %s from %s to %s: %s", mac, start_timestamp, end_timestamp, stats)
            return stats

if __name__ == '__main__':
    from db_ops.db_manager import DatabaseManager
    db_manager = DatabaseManager()
    scheduler = SchedulerManager(db_manager, check_interval=60)
    scheduler.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        scheduler.stop()
        logger.info("Scheduler terminated by user.")
