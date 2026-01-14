import json
import os
from typing import Dict, Optional


def get_connection_as_json(conn_id: str) -> str:
    secret = os.environ.get(conn_id)
    if not secret:
        raise ValueError(f"Секрет {conn_id} не найден в переменных окружения")
    return secret


def get_secret(conn_id: str) -> Dict:
    raw = get_connection_as_json(conn_id)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Секрет {conn_id} не является корректным JSON: {e}")