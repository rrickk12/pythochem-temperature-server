# DB Ops Module: Usage and API Documentation

## Overview

The **DB Ops** module provides an interface for managing sensor data in a relational database using SQLAlchemy. It offers CRUD operations for sensors, warnings, alert/schedule policies, as well as methods for inserting raw readings and aggregating them into cleaned or scheduled summaries.

## Package Structure

- **db_ops/models.py:**  
  Defines the database schema (Sensors, AlertPolicies, SchedulePolicies, Warnings, ReadRaw, ReadClean, and ReadScheduled).

- **db_ops/db_manager.py:**  
  Contains the `DatabaseManager` class which exposes methods to interact with the database.

- **manage_db.py:**  
  A command-line tool to initialize or clean the database.

## Getting Started

1. **Installation:**
   - Ensure you have Python 3 installed.
   - Install SQLAlchemy (e.g., via `pip install sqlalchemy`).

2. **Using the Database Manager in Your Code:**

   ```python
   from db_ops.db_manager import DatabaseManager

   # Initialize the manager (uses SQLite by default)
   db = DatabaseManager()

   # Insert a raw sensor reading
   db.insert_raw_read({
       "timestamp": "2025-04-14T16:47:26.532Z",
       "mac": "AC233FAE3005",
       "temperature": 26.42,
       "humidity": 60.52,
       "rssi": -39,
       "type": "MST01",
       "flags": ""
   })

   # Set an alert policy for the sensor
   db.set_alert_policy("AC233FAE3005", temp_min=15, temp_max=30, humidity_min=40, humidity_max=70)

   # Compress raw readings into a clean, one-minute aggregated record
   db.compress_minute_reads("AC233FAE3005", "2025-04-14T16:47")

   # Retrieve the latest raw readings
   latest_raw = db.get_latest_raw_reads("AC233FAE3005", limit=50)
   print(latest_raw)
