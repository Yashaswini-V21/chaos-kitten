import hashlib
import hmac
import base64

target_sig = "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
msg = b"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6ImFkbWluIiwiYWRtaW4iOnRydWV9"

def check(key):
    try:
        if isinstance(key, str):
            key = key.encode('utf-8')
        sig = base64.urlsafe_b64encode(hmac.new(key, msg, hashlib.sha256).digest()).decode().strip("=")
        if sig == target_sig:
            print(f"FOUND KEY: {key}")
            return True
    except: pass
    return False

# Attempt brute force variants
variants = [
    "secret", "secret\n", "secret\r\n", " secret", "secret ", "password", "123456",
    b"secret", base64.b64encode(b"secret"), 
    "weak_secret", "weak-secret", "changeme", "admin"
]

import itertools
for k in variants:
    if check(k): break

# Maybe the payload order was different but base64 strings looked surprisingly similar?
# e.g. {"admin":true,"name":"admin","sub":"1234567890"}
# eyJhZG1pbiI6dHJ1ZSwibmFtZSI6ImFkbWluIiwic3ViIjoiMTIzNDU2Nzg5MCJ9

payload2 = b'eyJhZG1pbiI6dHJ1ZSwibmFtZSI6ImFkbWluIiwic3ViIjoiMTIzNDU2Nzg5MCJ9' # {"admin":true...}
msg2 = b"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + payload2
# check(msg2, "secret") logic... but check function uses global msg.

def check_msg(m, key):
    k = key.encode() if isinstance(key, str) else key
    sig = base64.urlsafe_b64encode(hmac.new(k, m, hashlib.sha256).digest()).decode().strip("=")
    if sig == target_sig:
        print(f"FOUND! Msg: {m}, Key: {key}")
        return True
    return False

check_msg(msg2, "secret")

