# utils/parser.py
import json

def parse_payload(raw_payload):
    """
    @description
        Converts and validates raw BLE data payload into a structured Python object.
    @parameters
        - raw_payload: A dict, list, or JSON string representing sensor data.
    @output
        - The structured sensor data (Python object), unchanged if already parsed.
    """
    # If the payload is already a dict or list, simply return it.
    if isinstance(raw_payload, (dict, list)):
        return raw_payload
    # Otherwise, assume it's a JSON string and parse it.
    return json.loads(raw_payload)
