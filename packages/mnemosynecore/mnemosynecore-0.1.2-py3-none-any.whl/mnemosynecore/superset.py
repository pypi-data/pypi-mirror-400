import requests
from .vault import get_secret


def superset_request(
    *,
    endpoint: str,
    method: str = "GET",
    payload: dict | None = None,
    vault_conn_id: str
):

    cfg = get_secret(vault_conn_id)
    base_url = cfg["host"]

    headers = {
        "Authorization": f"Bearer {cfg['password']}",
        "Content-Type": "application/json",
    }

    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    resp = requests.request(method, url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()