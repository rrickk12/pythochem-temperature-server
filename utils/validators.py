# utils/validators.py

def validate_sensor_payload(payload):
    """
    Validates that the sensor payload contains the required keys.
    
    Parameters:
        payload (dict): Parsed sensor data.
    
    Returns:
        tuple: (is_valid (bool), errors (list))
    """
    required_keys = {'timestamp', 'mac', 'temperature', 'humidity', 'rssi', 'type', 'flags'}
    missing_keys = required_keys - payload.keys()
    if missing_keys:
        return False, [f"Missing key: {key}" for key in missing_keys]
    return True, []
