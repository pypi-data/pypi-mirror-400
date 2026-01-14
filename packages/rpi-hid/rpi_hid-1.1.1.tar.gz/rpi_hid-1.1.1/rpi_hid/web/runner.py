import subprocess
import signal

_current = None

def run_script(code):
    global _current
    stop_script()

    _current = subprocess.Popen(
        ["python3", "-u", "-"],
        stdin=subprocess.PIPE,
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL),
        text=True
    )
    _current.stdin.write(code)
    _current.stdin.close()

def stop_script():
    global _current
    if _current and _current.poll() is None:
        _current.terminate()
        _current = None
