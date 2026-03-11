"""
tester/runner.py
Exécute tous les tests et calcule les métriques QoS (latence avg/p95, taux d'erreur).
"""

import datetime
import statistics
from tester.tests import ALL_TESTS


def run_all() -> dict:
    """
    Lance tous les tests, collecte les résultats et calcule les métriques.
    Retourne un dict conforme à la structure de run définie dans le sujet.
    """
    results = []
    for test_fn in ALL_TESTS:
        try:
            result = test_fn()
        except Exception as exc:
            result = {
                "name": test_fn.__name__,
                "status": "ERROR",
                "latency_ms": 0,
                "details": str(exc),
            }
        results.append(result)

    # ── Métriques ────────────────────────────────────────────────────────────
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = len(results) - passed
    latencies = [r["latency_ms"] for r in results if r["latency_ms"] > 0]

    avg_latency = round(statistics.mean(latencies), 2) if latencies else 0
    p95_latency = round(
        sorted(latencies)[int(len(latencies) * 0.95) - 1], 2
    ) if len(latencies) >= 2 else avg_latency

    error_rate = round(failed / len(results), 3) if results else 0
    availability = "UP" if error_rate < 0.5 else "DEGRADED"

    return {
        "api": "API Géoplateforme IGN — Géocodage",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "error_rate": error_rate,
            "latency_ms_avg": avg_latency,
            "latency_ms_p95": p95_latency,
            "availability": availability,
        },
        "tests": results,
    }
