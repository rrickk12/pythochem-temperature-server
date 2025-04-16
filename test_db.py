#!/usr/bin/env python3
"""
Diagnostic script to list all sensors and verify latest readings, policies, and data integrity.
"""

from db_ops.db_manager import DatabaseManager

def run_diagnostics():
    db = DatabaseManager()

    all_sensors = db.get_all_sensors()

    if not all_sensors:
        print("❌ No sensors found in the database.")
        return

    for sensor in all_sensors:
        print("="*60)
        print(f"🛰️ Sensor: {sensor.name or 'Unnamed'}")
        print(f"🔧 MAC: {sensor.mac}")
        print(f"📍 Location: {sensor.location or 'N/A'}")
        print(f"⏱️ Last Read: {sensor.last_read or 'N/A'}")
        print()

        # Latest raw readings
        raw_reads = db.get_latest_clean_reads(sensor.mac, limit=5)
        if raw_reads:
            print("📊 Last Raw Readings:")
            for r in raw_reads:
                print(f" - {r.timestamp} | Temp: {r.temperature}°C | Hum: {r.humidity}% | RSSI: {r.rssi}")
        else:
            print("⚠️ No raw readings found.")

        # Alert policy check
        alert = db.get_alert_policy(sensor.mac)
        if alert:
            print(f"\n🚨 Alert Policy: Temp({alert.temp_min} - {alert.temp_max})°C | Hum({alert.humidity_min} - {alert.humidity_max})%")
        else:
            print("⚠️ No alert policy set.")

        # Schedule policy check
        schedule = db.get_schedule_policy(sensor.mac)
        if schedule:
            print(f"📅 Schedule Policy: Every {schedule.delta_time}s | Last Update: {schedule.last_update or 'N/A'}")
        else:
            print("⚠️ No schedule policy set.")

        print("="*60 + "\n")

if __name__ == "__main__":
    run_diagnostics()
