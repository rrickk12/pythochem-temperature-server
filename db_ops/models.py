# db_ops/models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Sensor(Base):
    __tablename__ = "sensors"
    mac = Column(String, primary_key=True)
    name = Column(String)
    location = Column(String)
    last_read = Column(String)
    is_active = Column(Boolean, default=True)
    
    # One-to-one relationships.
    alert_policy = relationship("AlertPolicy", back_populates="sensor", uselist=False)
    schedule_policy = relationship("SchedulePolicy", back_populates="sensor", uselist=False)
    # One-to-many relationships; cascades may be added as needed.
    warnings = relationship("Warning", back_populates="sensor", cascade="all, delete-orphan")
    raw_reads = relationship("ReadRaw", back_populates="sensor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sensor(mac={self.mac!r}, name={self.name!r}, last_read={self.last_read!r})>"


class AlertPolicy(Base):
    __tablename__ = "alert_policies"
    mac = Column(String, ForeignKey("sensors.mac"), primary_key=True)
    temp_max = Column(Float)
    temp_min = Column(Float)
    humidity_max = Column(Float)
    humidity_min = Column(Float)
    
    sensor = relationship("Sensor", back_populates="alert_policy")

    def __repr__(self):
        return (f"<AlertPolicy(mac={self.mac!r}, temp_min={self.temp_min!r}, "
                f"temp_max={self.temp_max!r}, humidity_min={self.humidity_min!r}, "
                f"humidity_max={self.humidity_max!r})>")


class SchedulePolicy(Base):
    __tablename__ = "schedule_policies"
    mac = Column(String, ForeignKey("sensors.mac"), primary_key=True)
    delta_time = Column(Integer)
    last_update = Column(String)
    
    sensor = relationship("Sensor", back_populates="schedule_policy")

    def __repr__(self):
        return f"<SchedulePolicy(mac={self.mac!r}, delta_time={self.delta_time}, last_update={self.last_update!r})>"


class Warning(Base):
    __tablename__ = "warnings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String)
    mac = Column(String, ForeignKey("sensors.mac"))
    type = Column(String)
    message = Column(Text)
    read = Column(Boolean, default=False)
    posted = Column(Boolean, default=False)
    
    sensor = relationship("Sensor", back_populates="warnings")

    def __repr__(self):
        return f"<Warning(id={self.id}, mac={self.mac!r}, type={self.type!r}, timestamp={self.timestamp!r})>"


class ReadRaw(Base):
    __tablename__ = "reads_raw"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String)
    mac = Column(String, ForeignKey("sensors.mac"))
    temperature = Column(Float)
    humidity = Column(Float)
    rssi = Column(Integer)
    type = Column(String)
    flags = Column(Text)
    
    sensor = relationship("Sensor", back_populates="raw_reads")

    def __repr__(self):
        return (f"<ReadRaw(id={self.id}, mac={self.mac!r}, timestamp={self.timestamp!r}, "
                f"temperature={self.temperature}, humidity={self.humidity})>")


class ReadClean(Base):
    __tablename__ = "reads_clean"
    timestamp = Column(String, primary_key=True)
    mac = Column(String, ForeignKey("sensors.mac"), primary_key=True)
    avg_temp = Column(Float)
    avg_hum = Column(Float)
    min_temp = Column(Float)
    max_temp = Column(Float)
    min_hum = Column(Float)
    max_hum = Column(Float)
    flags = Column(Text)

    def __repr__(self):
        return (f"<ReadClean(timestamp={self.timestamp!r}, mac={self.mac!r}, "
                f"avg_temp={self.avg_temp}, avg_hum={self.avg_hum})>")


class ReadScheduled(Base):
    __tablename__ = "reads_scheduled"
    timestamp = Column(String, primary_key=True)
    mac = Column(String, ForeignKey("sensors.mac"), primary_key=True)
    avg_temp = Column(Float)
    avg_hum = Column(Float)
    min_temp = Column(Float)
    max_temp = Column(Float)
    min_hum = Column(Float)
    max_hum = Column(Float)
    flags = Column(Text)

    def __repr__(self):
        return (f"<ReadScheduled(timestamp={self.timestamp!r}, mac={self.mac!r}, "
                f"avg_temp={self.avg_temp}, avg_hum={self.avg_hum})>")
