import subprocess
import signal
import sys
import os
import tempfile

_current = None

def run_script(code):
    global _current
    stop_script()

    python = sys.executable

    _current = subprocess.Popen(
        [python, "-u", "-"],
        stdin=subprocess.PIPE,
        text=True,
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL),
        env=os.environ.copy()
    )

    _current.stdin.write(code)
    _current.stdin.close()


def run_ducky(ducky_code):
    global _current
    stop_script()

    python = sys.executable

    fd, path = tempfile.mkstemp(suffix=".ducky")
    with os.fdopen(fd, "w") as f:
        f.write(ducky_code)

    _current = subprocess.Popen(
        [
            python,
            "-c",
            (
                "from rpi_hid.ducky import DuckyInterpreter;"
                f"d=DuckyInterpreter();"
                f"d.run_file('{path}');"
                f"d.close()"
            )
        ],
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL),
        env=os.environ.copy()
    )


def stop_script():
    global _current
    if _current and _current.poll() is None:
        _current.terminate()
        _current = None
