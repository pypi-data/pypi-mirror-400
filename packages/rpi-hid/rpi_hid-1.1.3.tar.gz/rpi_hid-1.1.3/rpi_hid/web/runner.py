import subprocess
import signal
import sys
import os

_current = None

def run_script(code):
    global _current
    stop_script()

    python = sys.executable  # ← USE VENV PYTHON

    _current = subprocess.Popen(
        [python, "-u", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL),
        env=os.environ.copy()
    )

    _current.stdin.write(code)
    _current.stdin.close()

def stop_script():
    global _current
    if _current and _current.poll() is None:
        _current.terminate()
        _current = None
