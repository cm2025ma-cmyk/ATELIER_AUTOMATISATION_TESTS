"""
tester/client.py
Wrapper HTTP : timeout, mesure de latence, retry simple, gestion 429/5xx.
"""

import time
import requests

BASE_URL = "https://data.geopf.fr/geocodage"
DEFAULT_TIMEOUT = 5  # secondes


def get(path: str, params: dict = None, retries: int = 1) -> dict:
    """
    Effectue un GET sur BASE_URL + path.
    Retourne un dict avec :
      - status_code (int)
      - json (dict | None)
      - latency_ms (float)
      - error (str | None)
    Gère : timeout, 429 (backoff 2s), 5xx, erreurs réseau.
    """
    url = BASE_URL + path
    attempt = 0

    while attempt <= retries:
        start = time.perf_counter()
        try:
            resp = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            latency_ms = (time.perf_counter() - start) * 1000

            # Gestion rate-limit : backoff et retry
            if resp.status_code == 429:
                if attempt < retries:
                    time.sleep(2)
                    attempt += 1
                    continue
                return {
                    "status_code": 429,
                    "json": None,
                    "latency_ms": round(latency_ms, 2),
                    "error": "Rate limited (429)",
                }

            # Tenter de parser le JSON
            try:
                body = resp.json()
            except Exception:
                body = None

            return {
                "status_code": resp.status_code,
                "json": body,
                "latency_ms": round(latency_ms, 2),
                "error": None,
            }

        except requests.Timeout:
            latency_ms = (time.perf_counter() - start) * 1000
            if attempt < retries:
                attempt += 1
                continue
            return {
                "status_code": None,
                "json": None,
                "latency_ms": round(latency_ms, 2),
                "error": "Timeout",
            }
        except requests.RequestException as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            return {
                "status_code": None,
                "json": None,
                "latency_ms": round(latency_ms, 2),
                "error": str(exc),
            }

    # Ne devrait pas arriver
    return {"status_code": None, "json": None, "latency_ms": 0, "error": "Unknown"}
