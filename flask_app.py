from flask import Flask, jsonify, render_template
from tester.runner import run_all
from storage import init_db, save_run, list_runs, get_last_run
import time

app = Flask(__name__)
init_db()

last_run_time = 0
MIN_INTERVAL = 300

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/run")
def run_tests():
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
    runs = list_runs(limit=20)
    last = get_last_run()
    return render_template("dashboard.html", runs=runs, last=last)

@app.route("/history")
def history():
    return jsonify(list_runs(limit=20))

@app.route("/health")
def health():
    last = get_last_run()
    if not last:
        return jsonify({"status": "no data yet"})
    return jsonify({
        "status": "ok",
        "last_run": last["timestamp"],
        "passed": last["passed"],
        "failed": last["failed"],
        "error_rate": last["error_rate"]
    })
EOFfrom flask import Flask, jsonify, render_template
from tester.runner import run_all
from storage import init_db, save_run, list_runs, get_last_run
import time

app = Flask(__name__)
init_db()

last_run_time = 0
MIN_INTERVAL = 300  # 5 minutes minimum entre deux runs

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/run")
def run_tests():
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
    runs = li
