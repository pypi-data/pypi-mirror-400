import os
import sys
import subprocess

SYSTEMD_DIR = "/etc/systemd/system"

def _service_name(script_path):
    name = os.path.basename(script_path).replace(".py", "")
    return f"rpi-hid-{name}.service"

def _service_path(service):
    return os.path.join(SYSTEMD_DIR, service)

def activate(script_path):
    service = _service_name(script_path)
    service_file = _service_path(service)

    # Absolute paths (critical for systemd)
    script_path = os.path.abspath(script_path)
    python = sys.executable   # venv python (IMPORTANT)

    content = f"""[Unit]
Description=RPI HID AutoStart ({service})
After=hid-gadget.service
Requires=hid-gadget.service

[Service]
Type=oneshot
ExecStart={python} {script_path}
WorkingDirectory={os.path.dirname(script_path)}
Restart=no
SuccessExitStatus=0
StandardOutput=append:/tmp/rpi_hid_autostart.log
StandardError=append:/tmp/rpi_hid_autostart.log

[Install]
WantedBy=multi-user.target
"""

    with open(service_file, "w") as f:
        f.write(content)

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", service], check=True)

    print(f"[+] AutoStart ENABLED for {script_path}")


def deactivate(script_path):
    service = _service_name(script_path)

    subprocess.run(["systemctl", "disable", service], check=False)
    subprocess.run(["systemctl", "stop", service], check=False)

    service_file = _service_path(service)
    if os.path.exists(service_file):
        os.remove(service_file)

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    print(f"[-] AutoStart DISABLED for {script_path}")

def list_autostart():
    print("Active RPI-HID AutoStart services:\n")
    for f in os.listdir(SYSTEMD_DIR):
        if f.startswith("rpi-hid-") and f.endswith(".service"):
            print(" •", f)
