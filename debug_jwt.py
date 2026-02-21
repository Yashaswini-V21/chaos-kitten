import jwt
import hashlib
import hmac
import base64

secret = "secret"
payload = {"sub": "1234567890", "name": "admin", "admin": True}

# PyJWT
try:
    token = jwt.encode(payload, secret, algorithm="HS256")
    print(f"PyJWT Token: {token}")
    
    parts = token.split('.')
    print(f"Header: {base64.urlsafe_b64decode(parts[0] + '==').decode()}")
    print(f"Payload: {base64.urlsafe_b64decode(parts[1] + '==').decode()}")
    print(f"Signature: {parts[2]}")

except Exception as e:
    print(f"Error: {e}")

# Reviewer's token signature check
reviewer_sig = "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
# My sig
my_sig = "44lJS0jlltzcglq7vgjXMXYRTecBxseN3Dec_LO_osI"

print(f"\nReviewer sig == My sig? {reviewer_sig == my_sig}")
