# generate_credentials.py
import random
import string

with open("user_credentials.txt", "w") as f:
    for i in range(1, 101):
        username = f"user{str(i).zfill(2)}"
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        f.write(f"{username}:{password}\n")
