#!/usr/bin/env python3
import os
import subprocess

CREDENTIAL_FILE = "/tmp/user_credentials.txt"

# Define group membership
admin_users = {"opn", "tyo"}
trainer_users = {"tyo", "dika", "oky", "hendri"}
trainee_prefix = "user"

# Create necessary groups
for group in ["admin", "trainer", "trainee"]:
    subprocess.run(["groupadd", "-f", group])

# Read credentials
with open(CREDENTIAL_FILE) as f:
    for line in f:
        line = line.strip()
        if not line or ":" not in line:
            continue

        user, password = line.split(":", 1)

        try:
            # Check if user exists
            subprocess.run(["id", user], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🧍 {user} already exists — skipping password setup")
        except subprocess.CalledProcessError:
            # Create user and set password
            subprocess.run(["useradd", "-m", "-s", "/bin/bash", "-U", user], check=True)
            subprocess.run(["chpasswd"], input=f"{user}:{password}".encode(), check=True)
            print(f"✅ Created user: {user}")

        # Add user to appropriate groups
        if user in admin_users:
            subprocess.run(["usermod", "-aG", "admin", user])
        if user in trainer_users:
            subprocess.run(["usermod", "-aG", "trainer", user])
        if user.startswith(trainee_prefix):
            subprocess.run(["usermod", "-aG", "trainee", user])

        # Ensure proper Jupyter runtime directory and permissions
        runtime_dir = f"/home/{user}/.local/share/jupyter/runtime"
        os.makedirs(runtime_dir, exist_ok=True)
        subprocess.run(["chown", "-R", f"{user}:{user}", f"/home/{user}/.local"])
        subprocess.run(["chown", "-R", f"{user}:{user}", f"/home/{user}"])