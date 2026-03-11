import requests
import time

BASE_URL = "https://data.geopf.fr/geocodage"

def get(endpoint, params=None, timeout=5, retries=1):
    """
    Envoie une requête GET à l'API BAN.
    - timeout : secondes max avant d'abandonner
    - retries : nombre de tentatives supplémentaires si erreur
    Retourne un dict avec : status, json, latency_ms, error
    """
    url = BASE_URL + endpoint
    attempt = 0

    while attempt <= retries:
        try:
            start = time.time()
            response = requests.get(url, params=params, timeout=timeout)
            latency_ms = round((time.time() - start) * 1000)

            # Gestion du rate limiting (429) : on attend et on réessaie
            if response.status_code == 429:
                time.sleep(2)
                attempt += 1
                continue

            return {
                "status": response.status_code,
                "json": response.json() if response.headers.get("Content-Type", "").startswith("application/json") else None,
                "latency_ms": latency_ms,
                "error": None
            }

        except requests.Timeout:
            attempt += 1
            if attempt > retries:
                return {"status": None, "json": None, "latency_ms": None, "error": "timeout"}

        except Exception as e:
            return {"status": None, "json": None, "latency_ms": None, "error": str(e)}

    return {"status": None, "json": None, "latency_ms": None, "error": "max retries reached"}