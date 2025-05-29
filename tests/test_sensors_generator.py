import requests
import random
import time
from datetime import datetime, timedelta

# Sensores existentes
SENSORS = [
    "AC233FC02377",
    "AC233FAE3041",
    "AC233FAE3002",
    "AC233FAE3040",
    "AC233FAE303E",
    "AC233FAE3005",
    "AC233FAE303F",
    "AC233FAE3004",
    "AC233FAE3003",
    "TESTMAC001",
]

# Config
URL = "http://127.0.0.1:5009/api/data/"  # Ajuste se necessário
INTERVAL = 2  # segundos entre cada envio por sensor
TEMP_RANGE = (20, 35)  # Temperatura em °C
HUM_RANGE  = (30, 80)  # Umidade em %

def random_reading(mac, dt):
    return {
        "mac": mac,
        "timestamp": dt.isoformat(),
        "temperature": round(random.uniform(*TEMP_RANGE), 1),
        "humidity": round(random.uniform(*HUM_RANGE), 1),
        "rssi": random.randint(-90, -30),
        "type": "test",
        "flags": ""
    }

if __name__ == "__main__":
    print("Enviando leituras simuladas para sensores... (Ctrl+C para parar)")
    try:
        while True:
            now = datetime.utcnow()
            batch = [random_reading(mac, now) for mac in SENSORS]
            resp = requests.post(URL, json=batch)
            print(f"[{now.isoformat()}] Enviados {len(batch)} leituras. Status: {resp.status_code}")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("Finalizado pelo usuário.")
