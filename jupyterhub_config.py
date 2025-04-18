from nativeauthenticator import NativeAuthenticator
import os

c = get_config()
c.JupyterHub.authenticator_class = 'jupyterhub.auth.PAMAuthenticator'

credential_file = "/tmp/user_credentials.txt"
allowed_users = set()

if os.path.exists(credential_file):
    with open(credential_file) as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            username = line.split(":", 1)[0]
            allowed_users.add(username)

# Assign to JupyterHub config
c.Authenticator.allowed_users = allowed_users
c.Authenticator.admin_users = {"opn", "tyo"}

# Disable user signup
c.NativeAuthenticator.create_users = False
c.NativeAuthenticator.enable_signup = False

# Spawner config
# c.JupyterHub.spawner_class = 'simple'
c.JupyterHub.spawner_class = 'jupyterhub.spawner.LocalProcessSpawner'
c.Spawner.default_url = '/lab'
c.Spawner.cmd = ['jupyter-labhub']
c.Spawner.notebook_dir = '/home/{username}'

import os
import shutil
import pwd
import grp

def multi_copy_templates(spawner):
    sources_targets = [
        ("/opt/marinemet-training/1_", "templates/1_"),
        ("/opt/marinemet-training/2_", "templates/2_"),
        ("/opt/marinemet-training/data", "templates/data")
    ]

    username = spawner.user.name
    home_dir = f"/home/{username}"

    uid = pwd.getpwnam(username).pw_uid
    gid = grp.getgrnam(username).gr_gid

    for template_dir, target_path in sources_targets:
        target_dir = os.path.join(home_dir, target_path)
        spawner.log.info(f"⏳ Copying templates from {template_dir} to {target_dir}")

        try:
            os.makedirs(target_dir, exist_ok=True)

            for item in os.listdir(template_dir):
                src = os.path.join(template_dir, item)
                dst = os.path.join(target_dir, item)

                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)

            # Fix ownership
            for root, dirs, files in os.walk(target_dir):
                for momo in dirs + files:
                    os.chown(os.path.join(root, momo), uid, gid)
            os.chown(target_dir, uid, gid)

            spawner.log.info(f"✅ Copied {template_dir} to {target_path}")

        except Exception as e:
            spawner.log.error(f"❌ Error copying {template_dir} to {target_path}: {e}")
            raise

c.Spawner.pre_spawn_hook = multi_copy_templates
