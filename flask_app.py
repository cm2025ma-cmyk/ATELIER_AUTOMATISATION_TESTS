from flask import Flask, render_template, jsonify
from tester.runner import run_all
from storage import init_db, save_run, list_runs, get_last_run
import time

app = Flask(__name__)
init_db()

last_run_time = 0
MIN_INTERVAL = 300  # 5 minutes entre deux runs

@app.route("/")
def consignes():
    return render_template('consignes.html')

@app.route("/run")
def run():
    global last_run_time
    now = time.time()
    if now - last_run_time < MIN_INTERVAL:
        wait = int(MIN_INTERVAL - (now - last_run_time))
        return jsonify({"error": f"Trop tôt, attends encore {wait}s"}), 429
    last_run_time = now
    result = run_all()
    save_run(result)
    return jsonify(result)

@app.route("/dashboard")
def dashboard():
    runs = list_
