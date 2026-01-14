from flask import Flask, render_template, request, jsonify
from .runner import run_script, run_ducky, stop_script

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("python.html")

# ---------- PYTHON ----------
@app.route("/python")
def python_page():
    return render_template("python.html")

@app.route("/python/run", methods=["POST"])
def python_run():
    code = request.json.get("code", "")
    run_script(code)
    return "", 204

# ---------- DUCKY ----------
@app.route("/ducky")
def ducky_page():
    return render_template("ducky.html")

@app.route("/ducky/run", methods=["POST"])
def ducky_run():
    code = request.json.get("code", "")
    run_ducky(code)
    return "", 204

# ---------- STOP ----------
@app.route("/stop", methods=["POST"])
def stop():
    stop_script()
    return "", 204


def run():
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    run()
