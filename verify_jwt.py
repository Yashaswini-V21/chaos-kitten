import jwt
import hashlib
import hmac
import base64

header = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
payload = 'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6ImFkbWluIiwiYWRtaW4iOnRydWV9'
signing_input = f"{header}.{payload}".encode()
key = b"secret"

signature = hmac.new(key, signing_input, hashlib.sha256).digest()
encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
print(f"Manual HMAC-SHA256 with 'secret': {encoded_signature}")

key2 = b"password"
signature2 = hmac.new(key2, signing_input, hashlib.sha256).digest()
encoded_signature2 = base64.urlsafe_b64encode(signature2).rstrip(b'=').decode()
print(f"Manual HMAC-SHA256 with 'password': {encoded_signature2}")

try:
    token = jwt.encode(
        {"sub": "1234567890", "name": "admin", "admin": True},
        "secret",
        algorithm="HS256"
    )
    print(f"PyJWT token: {token}")
except Exception as e:
    print(f"PyJWT error: {e}")
