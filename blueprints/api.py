import logging
from flask import Blueprint, request, jsonify, abort
from modules.service import sensor_service
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from io import BytesIO
from flask import send_file
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


def export_all_to_excel(json_data):
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Cabeçalhos humanizados
    headers = [
        ("timestamp", "Data e Hora"),
        ("avg_temp", "Temperatura Média (°C)"),
        ("avg_hum", "Umidade Média (%)"),
        ("min_temp", "Temp. Mín (°C)"),
        ("max_temp", "Temp. Máx (°C)"),
        ("min_hum", "Umid. Mín (%)"),
        ("max_hum", "Umid. Máx (%)"),
    ]

    header_fill = PatternFill(start_color="A7C7E7", end_color="A7C7E7", fill_type="solid")
    fill1 = PatternFill(start_color="F8FAFF", end_color="F8FAFF", fill_type="solid")
    fill2 = PatternFill(start_color="E5EDF7", end_color="E5EDF7", fill_type="solid")

    for mac, rows in json_data.items():
        ws = wb.create_sheet(title=mac[:31])  # Sheet title max 31 chars
        ws.append([h[1] for h in headers])

        # Estilo do cabeçalho
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col)
            cell.font = Font(bold=True)
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        # Dados com linhas zebradas
        for i, row in enumerate(rows, start=2):
            values = [row.get(key, "") for key, _ in headers]
            ws.append(values)
            fill = fill1 if i % 2 == 0 else fill2
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=i, column=col)
                cell.fill = fill
                cell.alignment = Alignment(horizontal="center")
                # Formatar números
                if col > 1:
                    try:
                        cell.value = float(cell.value)
                        cell.number_format = "0.00"
                    except (TypeError, ValueError):
                        pass

        # Congelar cabeçalho
        ws.freeze_panes = "A2"

        # Auto ajustar largura das colunas
        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

def export_one_to_excel(mac, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Sensor {mac}"

    # Cabeçalhos humanizados
    headers = [
        ("timestamp", "Data e Hora"),
        ("avg_temp", "Temperatura Média (°C)"),
        ("avg_hum", "Umidade Média (%)"),
        ("min_temp", "Temp. Mín (°C)"),
        ("max_temp", "Temp. Máx (°C)"),
        ("min_hum", "Umid. Mín (%)"),
        ("max_hum", "Umid. Máx (%)"),
    ]

    ws.append([h[1] for h in headers])

    # Estilo do cabeçalho
    header_fill = PatternFill(start_color="A7C7E7", end_color="A7C7E7", fill_type="solid")
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    # Dados com linhas zebradas
    fill1 = PatternFill(start_color="F8FAFF", end_color="F8FAFF", fill_type="solid")
    fill2 = PatternFill(start_color="E5EDF7", end_color="E5EDF7", fill_type="solid")

    for i, row in enumerate(rows, start=2):
        values = [row.get(key, "") for key, _ in headers]
        ws.append(values)
        fill = fill1 if i % 2 == 0 else fill2
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=i, column=col)
            cell.fill = fill
            cell.alignment = Alignment(horizontal="center")
            # Formatar números
            if col > 1:
                try:
                    cell.value = float(cell.value)
                    cell.number_format = "0.00"
                except (TypeError, ValueError):
                    pass

    # Congelar cabeçalho
    ws.freeze_panes = "A2"

    # Auto ajustar largura das colunas
    for col in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[get_column_letter(col[0].column)].width = max_length + 2

    # Exportar para BytesIO
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api/sensors')

def get_payload():
    data = request.get_json(silent=True)
    return data if data is not None else request.form.to_dict()

@api_bp.route('/', methods=['GET'])
def list_sensors():
    """GET /api/sensors/ — lista todos os sensores."""
    sensors = sensor_service.get_all_sensors()
    return jsonify([s.to_dict() for s in sensors]), 200

@api_bp.route('/<mac>', methods=['GET'])
def get_sensor(mac):
    """GET /api/sensors/<mac> — busca metadados de um sensor."""
    sensor = sensor_service.get_sensor(mac)
    if not sensor:
        abort(404)
    return jsonify(sensor.to_dict()), 200

@api_bp.route('/<mac>', methods=['PUT'])
def update_sensor(mac):
    """PUT /api/sensors/<mac> — renomeia um sensor."""
    data = get_payload()
    name = data.get('name')
    if not name:
        return jsonify({"error": "Missing 'name'"}), 400
    sensor_service.rename_sensor(mac, name)
    return jsonify({"status": "ok"}), 200

@api_bp.route('/<mac>/alarms', methods=['GET', 'PUT'])
def sensor_alarms(mac):
    """
    GET  /api/sensors/<mac>/alarms — retorna política de alarmes.
    PUT  /api/sensors/<mac>/alarms — atualiza política de alarmes.
    """
    if request.method == 'GET':
        policy = sensor_service.get_alert_policy(mac)
        return jsonify(policy), 200

    data = get_payload()
    required = ['temp_min','temp_max','humidity_min','humidity_max']
    if not all(k in data for k in required):
        return jsonify({"error": f"Missing one of {required}"}), 400

    result = sensor_service.update_sensor_alert_policy(
        mac,
        temp_min=data['temp_min'],
        temp_max=data['temp_max'],
        humidity_min=data['humidity_min'],
        humidity_max=data['humidity_max']
    )
    return jsonify(result), 200

@api_bp.route('/<mac>/schedules', methods=['GET','PUT'])
def sensor_schedules(mac):
    """
    GET  /api/sensors/<mac>/schedules — retorna política de agendamento.
    PUT  /api/sensors/<mac>/schedules — atualiza política de agendamento.
    """
    if request.method == 'GET':
        sched = sensor_service.get_schedule_policy(mac)
        return jsonify(sched), 200

    data = get_payload()
    delta = data.get('delta_time') or data.get('interval_hours')
    if not delta:
        return jsonify({"error": "Missing 'delta_time'"}), 400

    result = sensor_service.update_sensor_schedule_policy(mac, delta)
    return jsonify(result), 200

@api_bp.route('/<mac>/export', methods=['GET'])
def export_sensor(mac):
    """
    GET /api/sensors/<mac>/export?from=YYYY-MM-DD&to=YYYY-MM-DD&interval=H
    — exporta leituras formatadas (JSON ou CSV).
    """
    fr       = request.args.get('from')
    to       = request.args.get('to')
    interval = request.args.get('interval')
    if not all([fr, to, interval]):
        return jsonify({"error": "Missing parameters"}), 400

    data = sensor_service.export_sensor_data(mac, fr, to, interval)
    return jsonify(data), 200

@api_bp.route('/<mac>/report', methods=['GET'])
def sensor_report(mac):
    """
    GET /api/sensors/<mac>/report?start=...&end=...
    — gera e retorna relatório JSON.
    """
    start = request.args.get('start')
    end   = request.args.get('end')
    if not start or not end:
        return jsonify({"error": "Missing 'start' or 'end'"}), 400

    report = sensor_service.get_sensor_report(mac, start, end)
    return jsonify(report), 200

@api_bp.route('/export_all', methods=['GET'])
def export_all_sensors():
    """
    GET /api/sensors/export_all?from=...&to=...&interval=...
    — retorna agregados de todos os sensores no período.
    """
    fr = request.args.get('from')
    to = request.args.get('to')
    interval = request.args.get('interval')
    if not all([fr, to, interval]):
        return jsonify({"error": "Missing parameters"}), 400

    data = sensor_service.export_all_sensors_data(fr, to, interval)
    return jsonify(data), 200


@api_bp.route('/export_all_excel', methods=['GET'])
def export_all_excel():
    fr = request.args.get('from')
    to = request.args.get('to')
    interval = request.args.get('interval')
    if not all([fr, to, interval]):
        return jsonify({"error": "Missing parameters"}), 400

    data = sensor_service.export_all_sensors_data(fr, to, interval)
    buf = export_all_to_excel(data)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f'sensores_{fr}_a_{to}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@api_bp.route('/<mac>/export_excel', methods=['GET'])
def export_sensor_excel(mac):
    fr = request.args.get('from')
    to = request.args.get('to')
    interval = request.args.get('interval')
    if not all([fr, to, interval]):
        return jsonify({"error": "Missing parameters"}), 400

    rows = sensor_service.export_sensor_data(mac, fr, to, interval)
    buf = export_one_to_excel(mac, rows)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f'{mac}_{fr}_a_{to}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
