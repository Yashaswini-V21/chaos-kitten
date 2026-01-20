# 🐱 Chaos Kitten Demo API

> An intentionally vulnerable Flask API for testing Chaos Kitten

## ⚠️ WARNING

This API contains **INTENTIONAL security vulnerabilities** for educational and testing purposes.

- **DO NOT** deploy this in production
- **DO NOT** expose this to the internet
- Use only for local Chaos Kitten testing

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The API will be available at `http://localhost:5000`

## 🎯 Vulnerable Endpoints

| Endpoint | Method | Vulnerability |
|----------|--------|---------------|
| `/api/login` | POST | SQL Injection |
| `/api/users` | GET | Missing Authentication |
| `/api/users/<id>` | GET | IDOR |
| `/api/search?q=` | GET | SQL Injection |
| `/api/comments` | POST | Stored XSS |
| `/api/comments` | GET | Reflected XSS |
| `/api/admin/delete-user/<id>` | DELETE | Missing Auth |

## 🧪 Testing with Chaos Kitten

```bash
# From the project root
chaos-kitten scan --target http://localhost:5000 --spec examples/sample_openapi.json
```

## 📝 License

MIT - This is part of the Chaos Kitten project.
