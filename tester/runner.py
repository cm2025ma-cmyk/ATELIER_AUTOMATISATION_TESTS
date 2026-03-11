from tester.client import get

def make_result(name, passed, latency_ms, details=""):
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "latency_ms": latency_ms,
        "details": details
    }

def test_search_status_200():
    r = get("/search", params={"q": "8 bd du port", "limit": 1})
    return make_result(
        "GET /search retourne HTTP 200",
        r["status"] == 200,
        r["latency_ms"],
        f"status={r['status']}"
    )

def test_search_features_present():
    r = get("/search", params={"q": "Tour Eiffel Paris", "limit": 1})
    ok = r["json"] is not None and "features" in r["json"] and len(r["json"]["features"]) > 0
    return make_result(
        "Champ 'features' présent et non vide",
        ok,
        r["latency_ms"],
        "features manquant ou vide" if not ok else ""
    )

def test_search_label_is_string():
    r = get("/search", params={"q": "Paris", "limit": 1})
    try:
        label = r["json"]["features"][0]["properties"]["label"]
        ok = isinstance(label, str) and len(label) > 0
    except (KeyError, IndexError, TypeError):
        ok = False
    return make_result("properties.label est une string non vide", ok, r["latency_ms"])

def test_search_score_is_float():
    r = get("/search", params={"q": "Lyon", "limit": 1})
    try:
        score = r["json"]["features"][0]["properties"]["score"]
        ok = isinstance(score, float) and 0 <= score <= 1
    except (KeyError, IndexError, TypeError):
        ok = False
    return make_result("properties.score est un float entre 0 et 1", ok, r["latency_ms"])

def test_reverse_geocoding():
    r = get("/reverse", params={"lon": 2.3488, "lat": 48.8534})
    ok = r["status"] == 200 and r["json"] is not None and len(r["json"].get("features", [])) > 0
    return make_result("GET /reverse retourne une adresse valide", ok, r["latency_ms"])

def test_search_empty_query():
    r = get("/search", params={"q": "", "limit": 1})
    # On accepte 400 OU features vide (comportement défensif de l'API)
    ok = r["status"] == 400 or (
        r["json"] is not None and len(r["json"].get("features", [])) == 0
    )
    return make_result("Requête vide → erreur ou résultat vide", ok, r["latency_ms"])

# Liste de tous les tests à exécuter
ALL_TESTS = [
    test_search_status_200,
    test_search_features_present,
    test_search_label_is_string,
    test_search_score_is_float,
    test_reverse_geocoding,
    test_search_empty_query,
]
from datetime import datetime
import statistics

def run_all():
    results = []
    for test_fn in ALL_TESTS:
        result = test_fn()
        results.append(result)

    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    latencies = [r["latency_ms"] for r in results if r["latency_ms"] is not None]

    avg_latency = round(statistics.mean(latencies)) if latencies else None
    p95_latency = round(statistics.quantiles(latencies, n=20)[18]) if len(latencies) >= 2 else avg_latency

    return {
        "api": "Base Adresse Nationale",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": len(results),
            "error_rate": round(failed / len(results), 3),
            "latency_ms_avg": avg_latency,
            "latency_ms_p95": p95_latency,
        },
        "tests": results
    }

