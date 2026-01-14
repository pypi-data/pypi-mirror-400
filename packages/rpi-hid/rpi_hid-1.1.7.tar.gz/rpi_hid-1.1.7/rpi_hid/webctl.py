import os, sys, subprocess

SERVICE = "rpi-hid-web.service"
SYSTEMD = "/etc/systemd/system"

def enable_web():
    python = sys.executable
    content = f"""[Unit]
Description=RPI HID Web UI
After=network.target

[Service]
ExecStart={python} -m rpi_hid.web.app
Restart=always

[Install]
WantedBy=multi-user.target
"""
    path = os.path.join(SYSTEMD, SERVICE)
    with open(path, "w") as f:
        f.write(content)

    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", SERVICE], check=True)
    subprocess.run(["systemctl", "start", SERVICE], check=True)

def disable_web():
    subprocess.run(["systemctl", "stop", SERVICE], check=False)
    subprocess.run(["systemctl", "disable", SERVICE], check=False)
    try:
        os.remove(os.path.join(SYSTEMD, SERVICE))
    except FileNotFoundError:
        pass
    subprocess.run(["systemctl", "daemon-reload"], check=True)
