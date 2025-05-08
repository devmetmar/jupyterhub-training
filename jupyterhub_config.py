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
import stat

def multi_copy_templates(spawner):
    sources_targets = [
        ("/opt/marinemet-training/1_", "templates/1_"),
        ("/opt/marinemet-training/2_", "templates/2_"),
        ("/opt/marinemet-training/3_", "templates/3_"),
        ("/opt/marinemet-training/4_", "templates/4_"),
        ("/opt/marinemet-training/data", "templates/data"),
        ("/opt/marinemet-training/img", "templates/img")
    ]

    username = spawner.user.name
    home_dir = f"/home/{username}"
    templates_dir = os.path.join(home_dir, "templates")

    uid = pwd.getpwnam(username).pw_uid
    gid = grp.getgrnam(username).gr_gid

    # Ensure user owns the directory before deletion (in case root created it earlier)
    if os.path.exists(templates_dir):
        spawner.log.info(f"🗑️ Attempting to remove templates directory: {templates_dir}")
        try:
            spawner.log.info(f"🗑️ Attempting to remove templates directory: {templates_dir}")

            # Change permission to ensure it's deletable
            for root, dirs, files in os.walk(templates_dir):
                for momo in dirs + files:
                    path = os.path.join(root, momo)
                    try:
                        os.chmod(path, stat.S_IWUSR | stat.S_IRUSR | stat.S_IXUSR)
                    except Exception as chmod_err:
                        spawner.log.warning(f"⚠️ Failed to chmod {path}: {chmod_err}")

            shutil.rmtree(templates_dir)
            spawner.log.info(f"✅ Successfully removed: {templates_dir}")
        except Exception as e:
            spawner.log.error(f"❌ Error removing {templates_dir}: {e}")
            raise
    else:
        spawner.log.info(f"🗑️No need to remove templates directory: {templates_dir}")
        
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
