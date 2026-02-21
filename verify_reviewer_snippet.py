import jwt
token = jwt.encode(
    {"sub": "1234567890", "name": "admin", "admin": True},
    "secret",
    algorithm="HS256"
)
print(token)
