# db_ops/db_manager.py

import logging
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from db_ops.models import Base, Sensor, AlertPolicy, SchedulePolicy, Warning, ReadRaw, ReadClean, ReadScheduled
import datetime

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

    def get_scheduled_reads(self, mac, start, end):
        """
        Recupera leituras agregadas (ReadScheduled) para o sensor entre start e end (ISO 8601).
        """
        with self.Session() as session:
            reads = (session.query(ReadScheduled)
                            .filter_by(mac=mac)
                            .filter(ReadScheduled.timestamp >= start)
                            .filter(ReadScheduled.timestamp <= end)
                            .order_by(ReadScheduled.timestamp.asc())
                            .all())
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
        with self.Session() as session:
            policy = session.get(AlertPolicy, mac)
            if not policy:
                policy = AlertPolicy(mac=mac)
                session.add(policy)
                logger.debug("Created alert policy for sensor %s", mac)
            # Só atualiza se valor não é None (mantém os existentes caso não envie)
            if temp_min is not None:
                policy.temp_min = temp_min
            if temp_max is not None:
                policy.temp_max = temp_max
            if humidity_min is not None:
                policy.humidity_min = humidity_min
            if humidity_max is not None:
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
        with self.Session() as session:
            exists = session.query(ReadClean).filter_by(mac=mac, timestamp=minute_start).first()
            if exists:
                logger.debug("Already compressed for %s at %s", mac, minute_start)
                return

            # Pega todas as leituras daquele minuto, qualquer segundo/milissegundo/fuso
            prefix = minute_start  # '2025-05-29T16:42'
            rows = session.query(ReadRaw).filter(
                ReadRaw.mac == mac,
                ReadRaw.timestamp.like(f"{prefix}%")
            )
            count_raw = rows.count()
            if count_raw == 0:
                logger.debug("No RAWs for %s at %s", mac, minute_start)
                return

            aggregates = rows.with_entities(
                func.avg(ReadRaw.temperature).label("avg_temp"),
                func.avg(ReadRaw.humidity).label("avg_hum"),
                func.min(ReadRaw.temperature).label("min_temp"),
                func.max(ReadRaw.temperature).label("max_temp"),
                func.min(ReadRaw.humidity).label("min_hum"),
                func.max(ReadRaw.humidity).label("max_hum")
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
                logger.info("Compressed minute reads for sensor %s at %s (%d RAWs)", mac, minute_start, count_raw)

    
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

    def rename_sensor(self, mac, name):
        """
        Renames the sensor with the given MAC address.
        """
        with self.Session() as session:
            sensor = session.get(Sensor, mac)
            if sensor:
                sensor.name = name
                session.commit()
                logger.debug("Renamed sensor %s to '%s'", mac, name)
                return True
            else:
                logger.warning("Sensor %s not found for renaming.", mac)
                return False


def backfill_clean_reads(minutes=60*24):
    db = DatabaseManager()
    sensors = db.get_all_sensors()
    for sensor in sensors:
        print(f"Backfill {minutes} minutos para {sensor.mac}")
        count = 0
        for minute in range(minutes):
            ts = (datetime.datetime.utcnow() - datetime.timedelta(minutes=minute)).replace(second=0, microsecond=0)
            before = db.get_latest_clean_reads(sensor.mac, 1)
            db.compress_minute_reads(sensor.mac, ts.isoformat())
            after = db.get_latest_clean_reads(sensor.mac, 1)
            if len(after) > len(before):
                count += 1
        print(f"Sensor {sensor.mac}: {count} novos minutos agregados.")

def backfill_clean_reads_all():
    from db_ops.db_manager import DatabaseManager
    import datetime

    db = DatabaseManager()
    sensors = db.get_all_sensors()
    for sensor in sensors:
        print(f"Backfilling for sensor: {sensor.mac}")
        with db.Session() as session:
            min_ts = session.query(func.min(ReadRaw.timestamp)).filter(ReadRaw.mac == sensor.mac).scalar()
            max_ts = session.query(func.max(ReadRaw.timestamp)).filter(ReadRaw.mac == sensor.mac).scalar()
        if not min_ts or not max_ts:
            print(f"Nenhum dado RAW para {sensor.mac}. Pulando.")
            continue
        min_dt = datetime.datetime.fromisoformat(str(min_ts)[:16])  # até minutos
        max_dt = datetime.datetime.fromisoformat(str(max_ts)[:16])
        total_minutes = int((max_dt - min_dt).total_seconds() // 60)
        print(f"Sensor {sensor.mac}: {total_minutes} minutos de {min_dt} até {max_dt}")
        count = 0
        for m in range(total_minutes+1):
            ts = (min_dt + datetime.timedelta(minutes=m)).replace(second=0, microsecond=0)
            minute_str = ts.isoformat(timespec='minutes')
            db.compress_minute_reads(sensor.mac, minute_str)
            count += 1
            if count % 200 == 0:
                print(f"  {count} minutos processados...")
        print(f"Sensor {sensor.mac}: backfill concluído ({count} minutos).")
