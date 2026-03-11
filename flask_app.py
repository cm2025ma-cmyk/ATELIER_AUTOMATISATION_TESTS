from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)

@app.get("/")
def consignes():
     return render_template('consignes.html')
     
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
    # utile en local uniquement
    app.run(host="0.0.0.0", port=5000, debug=True)
