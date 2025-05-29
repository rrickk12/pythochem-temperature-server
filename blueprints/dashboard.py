# blueprints/dashboard.py

import logging
import json
from flask import Blueprint, render_template, abort
from db_ops.db_manager import DatabaseManager
from modules.service import sensor_service

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    db = DatabaseManager()
    sensors = sensor_service.get_all_sensors()
    cards = []

    for s in sensors:
        # 1) políticas vindas do DB (DBManager deve ter métodos semelhantes)
        alert_policy    = getattr(db, 'get_alert_policy', lambda mac: {}) (s.mac) or {}
        schedule_policy = getattr(db, 'get_schedule_policy', lambda mac: {}) (s.mac) or {}

        # 2) leituras e chart_data
        raws = (db.get_latest_clean_reads(s.mac, limit=10)
                or db.get_latest_raw_reads(s.mac, limit=10))
        chart_data = []
        for r in raws:
            chart_data.append({
                'timestamp': r.timestamp,
                'avg_temp':  getattr(r, 'avg_temp', None)  or getattr(r, 'temperature', None),
                'avg_hum':   getattr(r, 'avg_hum',  None)  or getattr(r, 'humidity',    None),
            })

        cards.append({
            'sensor':       s,
            'chart_data':   chart_data,
            'alert':        alert_policy,
            'schedule':     schedule_policy
        })

    return render_template('index.html', sensor_cards_data=cards)
