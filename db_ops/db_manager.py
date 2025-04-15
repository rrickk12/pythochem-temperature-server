# db_ops/db_manager.py

import logging
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from db_ops.models import Base, Sensor, AlertPolicy, SchedulePolicy, Warning, ReadRaw, ReadClean, ReadScheduled

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DatabaseManager:
    """
    Manages database operations, including CRUD for sensors, warnings, alert and schedule policies,
    as well as raw and aggregated readings.
    """
    def __init__(self, db_url='sqlite:///ble_data.db'):
        self.engine = create_engine(db_url, echo=False, future=True)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        Base.metadata.create_all(self.engine)
        logger.info("Database initialized with URL: %s", db_url)
    
    # -------------------------------
    # Sensor Methods
    # -------------------------------
    def insert_sensor_if_not_exists(self, mac, name=None, location=None):
        """
        Inserts a new sensor if it does not already exist.
        """
        with self.Session() as session:
            sensor = session.get(Sensor, mac)
            if sensor is None:
                sensor = Sensor(mac=mac, name=name, location=location)
                session.add(sensor)
                session.commit()
                logger.debug("Inserted new sensor: %s", sensor)
            else:
                logger.debug("Sensor already exists: %s", sensor)
    
    def update_sensor_last_read(self, mac, timestamp):
        """
        Updates the last reading timestamp of the sensor.
        """
        with self.Session() as session:
            sensor = session.get(Sensor, mac)
            if sensor:
                sensor.last_read = timestamp
                session.commit()
                logger.debug("Updated sensor %s last_read to %s", mac, timestamp)
            else:
                logger.warning("Sensor %s not found during update.", mac)
    
    def get_sensor(self, mac):
        """
        Retrieves a sensor record by MAC address.
        """
        with self.Session() as session:
            sensor = session.get(Sensor, mac)
            logger.debug("Retrieved sensor %s: %s", mac, sensor)
            return sensor
    
    def get_all_sensors(self):
        """
        Retrieves all sensor records.
        """
        with self.Session() as session:
            sensors = session.query(Sensor).all()
            logger.debug("Retrieved all sensors: %s", sensors)
            return sensors
    
    # -------------------------------
    # Raw Reading Methods
    # -------------------------------
    def insert_raw_read(self, data: dict):
        """
        Inserts a new raw reading.
        Expected data keys: 'timestamp', 'mac', 'temperature', 'humidity', 'rssi', 'type', 'flags'.
        """
        allowed_keys = {"timestamp", "mac", "temperature", "humidity", "rssi", "type", "flags"}
        sanitized_data = {k: data[k] for k in allowed_keys if k in data}
        with self.Session() as session:
            # Ensure sensor exists and update its last read timestamp.
            self.insert_sensor_if_not_exists(sanitized_data.get("mac"))
            self.update_sensor_last_read(sanitized_data.get("mac"), sanitized_data.get("timestamp"))
            read = ReadRaw(**sanitized_data)
            session.add(read)
            session.commit()
            logger.debug("Inserted raw read for sensor %s: %s", sanitized_data.get("mac"), read)
    
    def get_latest_raw_reads(self, mac, limit=100):
        """
        Retrieves the latest raw readings for the given sensor.
        """
        with self.Session() as session:
            reads = (session.query(ReadRaw)
                           .filter_by(mac=mac)
                           .order_by(ReadRaw.timestamp.desc())
                           .limit(limit)
                           .all())
            logger.debug("Retrieved latest %s raw reads for sensor %s: %s", limit, mac, reads)
            return reads
    
    def delete_old_raw_reads(self, mac, older_than_timestamp):
        """
        Deletes raw readings for a sensor that are older than the specified timestamp.
        Returns the number of records deleted.
        """
        with self.Session() as session:
            count = session.query(ReadRaw).filter(
                ReadRaw.mac == mac,
                ReadRaw.timestamp < older_than_timestamp
            ).delete()
            session.commit()
            logger.debug("Deleted %s raw reads for sensor %s older than %s", count, mac, older_than_timestamp)
            return count
    
    def get_latest_clean_reads(self, mac, limit=100):
        """
        Retrieves the latest clean (aggregated) readings for a sensor.
        """
        with self.Session() as session:
            reads = (session.query(ReadClean)
                           .filter_by(mac=mac)
                           .order_by(ReadClean.timestamp.desc())
                           .limit(limit)
                           .all())
            logger.debug("Retrieved latest %s clean reads for sensor %s: %s", limit, mac, reads)
            return reads
    
    # -------------------------------
    # Warning Methods
    # -------------------------------
    def insert_warning(self, warning_data: dict):
        """
        Inserts a new warning record.
        """
        with self.Session() as session:
            warning = Warning(**warning_data)
            session.add(warning)
            session.commit()
            logger.debug("Inserted warning: %s", warning)
    
    def get_warnings(self, mac=None):
        """
        Retrieves warning records. If a MAC address is provided, filters warnings for that sensor.
        """
        with self.Session() as session:
            query = session.query(Warning)
            if mac:
                query = query.filter_by(mac=mac)
            warnings = query.all()
            logger.debug("Retrieved warnings for sensor %s: %s", mac, warnings)
            return warnings
    
    # -------------------------------
    # Alert Policy Methods
    # -------------------------------
    def set_alert_policy(self, mac, temp_min=None, temp_max=None, humidity_min=None, humidity_max=None):
        """
        Sets or updates the alert policy thresholds for a sensor.
        """
        with self.Session() as session:
            policy = session.get(AlertPolicy, mac)
            if not policy:
                policy = AlertPolicy(mac=mac)
                session.add(policy)
                logger.debug("Created alert policy for sensor %s", mac)
            policy.temp_min = temp_min
            policy.temp_max = temp_max
            policy.humidity_min = humidity_min
            policy.humidity_max = humidity_max
            session.commit()
            logger.debug("Set alert policy for sensor %s: %s", mac, policy)
    
    def get_alert_policy(self, mac):
        """
        Retrieves the alert policy for a sensor.
        """
        with self.Session() as session:
            policy = session.query(AlertPolicy).filter_by(mac=mac).first()
            logger.debug("Retrieved alert policy for sensor %s: %s", mac, policy)
            return policy
    
    # -------------------------------
    # Schedule Policy Methods
    # -------------------------------
    def set_schedule_policy(self, mac, delta_time):
        """
        Sets or updates the schedule policy time interval for a sensor.
        """
        with self.Session() as session:
            policy = session.get(SchedulePolicy, mac)
            if not policy:
                policy = SchedulePolicy(mac=mac)
                session.add(policy)
                logger.debug("Created schedule policy for sensor %s", mac)
            policy.delta_time = delta_time
            session.commit()
            logger.debug("Set schedule policy for sensor %s: %s", mac, policy)
    
    def get_schedule_policy(self, mac):
        """
        Retrieves the schedule policy for a sensor.
        """
        with self.Session() as session:
            policy = session.query(SchedulePolicy).filter_by(mac=mac).first()
            logger.debug("Retrieved schedule policy for sensor %s: %s", mac, policy)
            return policy
    
    def update_schedule_policy_last_update(self, mac, timestamp):
        """
        Updates the last update timestamp for a sensor's schedule policy.
        """
        with self.Session() as session:
            policy = session.get(SchedulePolicy, mac)
            if policy:
                policy.last_update = timestamp
                session.commit()
                logger.debug("Updated schedule policy last_update for sensor %s to %s", mac, timestamp)
            else:
                logger.warning("Schedule policy for sensor %s not found.", mac)
    
    # -------------------------------
    # Readings Compression Methods
    # -------------------------------
    def compress_minute_reads(self, mac, minute_start):
        """
        Aggregates all raw readings for a sensor within a specific minute into a single clean reading.
        The minute_start timestamp should be formatted as "YYYY-MM-DDTHH:MM".
        """
        with self.Session() as session:
            aggregates = session.query(
                func.avg(ReadRaw.temperature).label("avg_temp"),
                func.avg(ReadRaw.humidity).label("avg_hum"),
                func.min(ReadRaw.temperature).label("min_temp"),
                func.max(ReadRaw.temperature).label("max_temp"),
                func.min(ReadRaw.humidity).label("min_hum"),
                func.max(ReadRaw.humidity).label("max_hum")
            ).filter(
                ReadRaw.mac == mac,
                ReadRaw.timestamp.between(f"{minute_start}:00", f"{minute_start}:59")
            ).first()
            if aggregates and aggregates.avg_temp is not None:
                clean_read = ReadClean(
                    timestamp=minute_start,
                    mac=mac,
                    avg_temp=aggregates.avg_temp,
                    avg_hum=aggregates.avg_hum,
                    min_temp=aggregates.min_temp,
                    max_temp=aggregates.max_temp,
                    min_hum=aggregates.min_hum,
                    max_hum=aggregates.max_hum,
                    flags=""
                )
                session.add(clean_read)
                session.commit()
                logger.debug("Compressed minute reads for sensor %s at %s: %s", mac, minute_start, clean_read)
    
    def compress_schedule_reads(self, mac, start_timestamp, end_timestamp):
        """
        Aggregates raw readings for a sensor over a specified interval into a scheduled reading.
        """
        with self.Session() as session:
            aggregates = session.query(
                func.avg(ReadRaw.temperature).label("avg_temp"),
                func.avg(ReadRaw.humidity).label("avg_hum"),
                func.min(ReadRaw.temperature).label("min_temp"),
                func.max(ReadRaw.temperature).label("max_temp"),
                func.min(ReadRaw.humidity).label("min_hum"),
                func.max(ReadRaw.humidity).label("max_hum")
            ).filter(
                ReadRaw.mac == mac,
                ReadRaw.timestamp.between(start_timestamp, end_timestamp)
            ).first()
            if aggregates and aggregates.avg_temp is not None:
                scheduled_read = ReadScheduled(
                    timestamp=start_timestamp,
                    mac=mac,
                    avg_temp=aggregates.avg_temp,
                    avg_hum=aggregates.avg_hum,
                    min_temp=aggregates.min_temp,
                    max_temp=aggregates.max_temp,
                    min_hum=aggregates.min_hum,
                    max_hum=aggregates.max_hum,
                    flags=""
                )
                session.add(scheduled_read)
                session.commit()
                logger.debug("Compressed schedule reads for sensor %s from %s to %s: %s",
                             mac, start_timestamp, end_timestamp, scheduled_read)
