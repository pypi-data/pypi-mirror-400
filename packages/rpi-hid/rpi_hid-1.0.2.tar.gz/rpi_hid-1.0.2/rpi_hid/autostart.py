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

    python = sys.executable
    script_path = os.path.abspath(script_path)

    content = f"""[Unit]
Description=RPI HID AutoStart ({service})
After=multi-user.target

[Service]
Type=simple
ExecStart={python} {script_path}
Restart=no

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
