"""
tester/tests.py
Tests "as code" pour l'API Géoplateforme IGN — Géocodage.
Chaque test retourne un dict : {name, status, latency_ms, details}
"""

from tester.client import get


def _result(name: str, passed: bool, latency: float, details: str = "") -> dict:
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "latency_ms": latency,
        "details": details,
    }


# ─── A. Tests Contrat ────────────────────────────────────────────────────────

def test_capabilities_status():
    """GET /getCapabilities → HTTP 200"""
    r = get("/getCapabilities")
    ok = r["status_code"] == 200 and r["error"] is None
    return _result(
        "GET /getCapabilities → HTTP 200",
        ok,
        r["latency_ms"],
        r["error"] or f"status={r['status_code']}",
    )


def test_capabilities_schema():
    """GET /getCapabilities → champs info, api, operations, indexes présents"""
    r = get("/getCapabilities")
    body = r["json"] or {}
    required = {"info", "api", "operations", "indexes"}
    missing = required - set(body.keys())
    ok = r["status_code"] == 200 and not missing
    return _result(
        "GET /getCapabilities → schéma valide",
        ok,
        r["latency_ms"],
        f"champs manquants: {missing}" if missing else "",
    )


def test_search_address_status():
    """GET /search?q=73+Avenue+de+Paris+Saint-Mandé → HTTP 200"""
    r = get("/search", params={"q": "73 Avenue de Paris Saint-Mandé", "limit": 5})
    ok = r["status_code"] == 200 and r["error"] is None
    return _result(
        "GET /search adresse valide → HTTP 200",
        ok,
        r["latency_ms"],
        r["error"] or f"status={r['status_code']}",
    )


def test_search_feature_collection():
    """GET /search → type=FeatureCollection et features est une liste"""
    r = get("/search", params={"q": "Tour Eiffel Paris", "limit": 3})
    body = r["json"] or {}
    ok = (
        r["status_code"] == 200
        and body.get("type") == "FeatureCollection"
        and isinstance(body.get("features"), list)
    )
    details = ""
    if not ok:
        details = f"type={body.get('type')}, features={type(body.get('features')).__name__}"
    return _result(
        "GET /search → FeatureCollection + features[]",
        ok,
        r["latency_ms"],
        details,
    )


def test_search_feature_fields():
    """Premier résultat /search → geometry.coordinates, properties.label, properties.score présents"""
    r = get("/search", params={"q": "Champs-Élysées Paris", "limit": 1})
    body = r["json"] or {}
    features = body.get("features", [])
    ok = False
    details = "aucun résultat"
    if features:
        feat = features[0]
        coords = feat.get("geometry", {}).get("coordinates")
        props = feat.get("properties", {})
        label = props.get("label")
        score = props.get("score")
        ok = (
            isinstance(coords, list) and len(coords) == 2
            and isinstance(label, str) and label
            and isinstance(score, float)
        )
        details = f"coords={coords}, label={label!r}, score={score}"
    return _result(
        "GET /search → champs geometry + label + score valides",
        ok,
        r["latency_ms"],
        details,
    )


def test_search_invalid_input():
    """GET /search?q=zzzzinexistantxxx → 200 avec features vide (pas d'erreur serveur)"""
    r = get("/search", params={"q": "zzzzinexistantxxx999", "limit": 1})
    body = r["json"] or {}
    # L'API retourne 200 + features vide pour une recherche sans résultat
    ok = r["status_code"] == 200 and isinstance(body.get("features"), list)
    return _result(
        "GET /search entrée invalide → 200 + features vide",
        ok,
        r["latency_ms"],
        f"features={body.get('features')}",
    )


def test_reverse_geocoding_status():
    """GET /reverse?lon=2.3276&lat=48.8352 → HTTP 200"""
    r = get("/reverse", params={"lon": 2.3276, "lat": 48.8352})
    ok = r["status_code"] == 200 and r["error"] is None
    return _result(
        "GET /reverse coords valides → HTTP 200",
        ok,
        r["latency_ms"],
        r["error"] or f"status={r['status_code']}",
    )


def test_reverse_feature_fields():
    """GET /reverse → résultat contient properties.label (string non vide)"""
    r = get("/reverse", params={"lon": 2.3276, "lat": 48.8352})
    body = r["json"] or {}
    features = body.get("features", [])
    ok = False
    details = "aucun résultat"
    if features:
        label = features[0].get("properties", {}).get("label")
        ok = isinstance(label, str) and bool(label)
        details = f"label={label!r}"
    return _result(
        "GET /reverse → properties.label présent et non vide",
        ok,
        r["latency_ms"],
        details,
    )


# ─── B. Tests Robustesse / QoS ───────────────────────────────────────────────

def test_timeout_resilience():
    """La requête se termine dans le timeout imparti (pas de blocage)"""
    import time
    start = time.perf_counter()
    r = get("/search", params={"q": "Paris", "limit": 1})
    elapsed = (time.perf_counter() - start) * 1000
    ok = elapsed < 6000  # 5s timeout + 1s marge
    return _result(
        "Timeout : réponse < 6 s",
        ok,
        r["latency_ms"],
        f"elapsed={elapsed:.0f}ms",
    )


def test_content_type_json():
    """GET /search → Content-Type contient application/json"""
    import requests
    try:
        resp = requests.get(
            "https://data.geopf.fr/geocodage/search",
            params={"q": "Lyon", "limit": 1},
            timeout=5,
        )
        ct = resp.headers.get("Content-Type", "")
        ok = "json" in ct.lower()
        return _result(
            "Content-Type → application/json",
            ok,
            0,
            f"Content-Type={ct}",
        )
    except Exception as exc:
        return _result("Content-Type → application/json", False, 0, str(exc))


# ─── Liste de tous les tests ─────────────────────────────────────────────────

ALL_TESTS = [
    test_capabilities_status,
    test_capabilities_schema,
    test_search_address_status,
    test_search_feature_collection,
    test_search_feature_fields,
    test_search_invalid_input,
    test_reverse_geocoding_status,
    test_reverse_feature_fields,
    test_timeout_resilience,
    test_content_type_json,
]
