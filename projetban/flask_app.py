from flask import Flask, jsonify, render_template
from tester.runner import run_all
from storage import init_db, save_run, list_runs

app = Flask(__name__)

# Initialise la base au démarrage
init_db()

@app.route("/run")
def run():
    """Déclenche un run de tests et sauvegarde le résultat."""
    result = run_all()
    save_run(result)
    return jsonify(result)

@app.route("/dashboard")
def dashboard():
    """Affiche le tableau de bord avec l'historique des runs."""
    runs = list_runs(limit=20)
    last = runs[0] if runs else None
    return render_template("dashboard.html", runs=runs, last=last)

@app.route("/health")
def health():
    """Endpoint bonus : état de santé rapide de la solution."""
    runs = list_runs(limit=1)
    if not runs:
        return jsonify({"status": "no runs yet"}), 200
    last = runs[0]
    status = "ok" if last["error_rate"] < 0.5 else "degraded"
    return jsonify({
        "status": status,
        "last_run": last["timestamp"],
        "error_rate": last["error_rate"],
        "latency_avg_ms": last["latency_avg"]
    })

if __name__ == "__main__":
    app.run(debug=True)
```

---

### 📄 Fichier 6 — `requirements.txt`
```
flask
requests