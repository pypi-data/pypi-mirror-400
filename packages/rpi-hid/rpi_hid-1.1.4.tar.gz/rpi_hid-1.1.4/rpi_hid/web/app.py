from flask import Flask, render_template, request, redirect, url_for
from .runner import run_script, run_ducky, stop_script

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for("python_page"))

@app.route("/python", methods=["GET", "POST"])
def python_page():
    if request.method == "POST":
        action = request.form.get("action")
        code = request.form.get("code", "")
        if action == "run":
            run_script(code)
        elif action == "stop":
            stop_script()
    return render_template("python.html")

@app.route("/ducky", methods=["GET", "POST"])
def ducky_page():
    if request.method == "POST":
        action = request.form.get("action")
        code = request.form.get("code", "")

        if action == "run":
            run_ducky(code)
        elif action == "stop":
            stop_script()
    return render_template("ducky.html")



def run():
    # BLOCKING – systemd requires this
    app.run(host="0.0.0.0", port=5000, debug=False)
