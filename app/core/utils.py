import datetime

def get_timestamp():
    """Devuelve el timestamp actual."""
    return datetime.datetime.now().isoformat()
