from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Sensor(Base):
    __tablename__ = "Sensors"
    mac = Column(String, primary_key=True)
    name = Column(String)
    location = Column(String)
    last_read = Column(String)
    is_active = Column(Boolean, default=True)

    alert_policy = relationship("AlertPolicy", back_populates="sensor", uselist=False)
    schedule_policy = relationship("SchedulePolicy", back_populates="sensor", uselist=False)
    warnings = relationship("Warning", back_populates="sensor")
    raw_reads = relationship("ReadRaw", back_populates="sensor")

class AlertPolicy(Base):
    __tablename__ = "AlertPolicies"
    mac = Column(String, ForeignKey("Sensors.mac"), primary_key=True)
    temp_max = Column(Float)
    temp_min = Column(Float)
    humidity_max = Column(Float)
    humidity_min = Column(Float)

    sensor = relationship("Sensor", back_populates="alert_policy")

class SchedulePolicy(Base):
    __tablename__ = "SchedulePolicies"
    mac = Column(String, ForeignKey("Sensors.mac"), primary_key=True)
    delta_time = Column(Integer)
    last_update = Column(String)

    sensor = relationship("Sensor", back_populates="schedule_policy")

class Warning(Base):
    __tablename__ = "Warnings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String)
    mac = Column(String, ForeignKey("Sensors.mac"))
    type = Column(String)
    message = Column(Text)
    read = Column(Boolean, default=False)
    posted = Column(Boolean, default=False)

    sensor = relationship("Sensor", back_populates="warnings")

class ReadRaw(Base):
    __tablename__ = "ReadsRaw"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String)
    mac = Column(String, ForeignKey("Sensors.mac"))
    temperature = Column(Float)
    humidity = Column(Float)
    rssi = Column(Integer)
    type = Column(String)
    flags = Column(Text)

    sensor = relationship("Sensor", back_populates="raw_reads")

class ReadClean(Base):
    __tablename__ = "ReadsClean"
    timestamp = Column(String, primary_key=True)
    mac = Column(String, ForeignKey("Sensors.mac"), primary_key=True)
    avg_temp = Column(Float)
    avg_hum = Column(Float)
    min_temp = Column(Float)
    max_temp = Column(Float)
    min_hum = Column(Float)
    max_hum = Column(Float)
    flags = Column(Text)

class ReadScheduled(Base):
    __tablename__ = "ReadsScheduled"
    timestamp = Column(String, primary_key=True)
    mac = Column(String, ForeignKey("Sensors.mac"), primary_key=True)
    avg_temp = Column(Float)
    avg_hum = Column(Float)
    min_temp = Column(Float)
    max_temp = Column(Float)
    min_hum = Column(Float)
    max_hum = Column(Float)
    flags = Column(Text)
