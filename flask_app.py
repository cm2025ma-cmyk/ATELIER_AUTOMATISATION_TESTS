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

@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/run")
def run_tests():
    """Déclenche un run complet, le persiste et retourne le résultat en JSON."""
    result = run_all()
    run_id = storage.save_run(result)
    result["run_id"] = run_id
    return jsonify(result)


@app.route("/dashboard")
def dashboard():
    """Tableau de bord : dernier run + historique des 20 derniers runs."""
    latest = storage.get_latest_run()
    history = storage.list_runs(limit=20)
    return render_template("dashboard.html", latest=latest, history=history)


@app.route("/health")
def health():
    """Endpoint de santé : vérifie que la DB est accessible et retourne le statut."""
    try:
        history = storage.list_runs(limit=1)
        last_run = history[0] if history else None
        return jsonify({
            "status": "ok",
            "db": "reachable",
            "last_run_id": last_run["id"] if last_run else None,
            "last_availability": last_run["availability"] if last_run else "N/A",
        })
    except Exception as exc:
        return jsonify({"status": "error", "detail": str(exc)}), 500


@app.route("/export")
def export():
    """Télécharge le dernier run au format JSON."""
    latest = storage.get_latest_run()
    if not latest:
        return jsonify({"error": "Aucun run disponible"}), 404
    response = app.response_class(
        response=json.dumps(latest, ensure_ascii=False, indent=2),
        status=200,
        mimetype="application/json",
    )
    response.headers["Content-Disposition"] = "attachment; filename=last_run.json"
    return response


if __name__ == "__main__":
    app.run(debug=True)



