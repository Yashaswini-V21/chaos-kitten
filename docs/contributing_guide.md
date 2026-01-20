# 🤝 Contributing to Chaos Kitten

First off, thanks for taking the time to contribute! 🎉

Chaos Kitten is designed to be **beginner-friendly**. Whether you're a seasoned security researcher or just getting started with open source, there's a place for you here.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [🐣 First-Timers (No Coding Required)](#-first-timers-no-coding-required)
  - [🐥 Beginners (Basic Python)](#-beginners-basic-python)
  - [🐔 Intermediate Contributors](#-intermediate-contributors)
  - [🦅 Advanced Contributors](#-advanced-contributors)
- [Development Setup](#development-setup)
- [Creating Attack Profiles](#creating-attack-profiles)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)

---

## Code of Conduct

Be kind and respectful. We're all here to learn and build something awesome together. 🐱

---

## How Can I Contribute?

### 🐣 First-Timers (No Coding Required!)

Perfect for your first ever open source contribution:

1. **Add Naughty Strings**
   - Edit `toys/data/naughty_strings.json`
   - Add strings that might break applications (empty strings, unicode, special chars)

2. **Add Attack Payloads**
   - Add new SQL injection payloads to `toys/sql_injection_basic.yaml`
   - Add XSS payloads to `toys/xss_reflected.yaml`

3. **Improve Documentation**
   - Fix typos in README or docs
   - Add examples
   - Translate documentation

### 🐥 Beginners (Basic Python)

Great for those learning Python:

1. **Create New Attack Profiles**
   ```yaml
   # Create a new file in toys/ folder
   name: "My Attack Profile"
   category: "injection"
   severity: "high"
   payloads:
     - "payload1"
     - "payload2"
   ```

2. **Write Unit Tests**
   - Add tests in `tests/` folder
   - Test specific payloads or functions

3. **CLI Improvements**
   - Add colors to terminal output
   - Improve help messages

### 🐔 Intermediate Contributors

For those comfortable with Python:

1. **Implement New Attack Strategies**
   - JWT token manipulation
   - GraphQL injection
   - API rate limiting bypass

2. **Enhance Browser Automation**
   - Improve Playwright XSS detection
   - Add screenshot capture for evidence

3. **Parser Improvements**
   - Add support for AsyncAPI
   - Handle edge cases in OpenAPI parsing

### 🦅 Advanced Contributors

For experienced developers:

1. **Multi-step Exploits**
   - Chain attacks together (e.g., IDOR → Privilege Escalation)
   - Implement attack graphs

2. **LLM Optimization**
   - Improve prompt engineering
   - Add support for new LLM providers

3. **Infrastructure**
   - Kubernetes Operator
   - GitHub Actions integration

---

## Development Setup

```bash
# Clone the repository
git clone https://github.com/mdhaarishussain/chaos-kitten.git
cd chaos-kitten

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run the demo API for testing
cd examples/demo_api
python app.py
```

---

## Creating Attack Profiles

Attack profiles are YAML files in the `toys/` folder. Here's the structure:

```yaml
# toys/my_attack.yaml
name: "Attack Name"
category: "injection"  # injection, access_control, cryptography, etc.
severity: "critical"   # critical, high, medium, low
description: "What this attack tests for"

target_fields:
  - "username"
  - "password"
  - "search"

payloads:
  - "payload1"
  - "payload2"

success_indicators:
  - "error message"
  - status_code: 500

remediation: |
  How to fix this vulnerability:
  1. Step one
  2. Step two

cat_message: "Playful message when vulnerability found 🐱"
```

---

## Submitting Changes

1. **Fork the Repository**
   Click the "Fork" button on GitHub

2. **Create a Branch**
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

3. **Make Your Changes**
   - Write code
   - Add tests
   - Update documentation

4. **Commit with Good Messages**
   ```bash
   git commit -m "feat: add JWT token manipulation attack"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/my-awesome-feature
   ```
   Then open a Pull Request on GitHub

---

## Style Guidelines

### Python
- Use [Black](https://github.com/psf/black) for formatting
- Follow PEP 8
- Type hints encouraged

### YAML Attack Profiles
- Use descriptive names
- Include remediation guidance
- Add cat-themed messages! 🐱

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring

---

## 🎉 Thank You!

Every contribution helps make Chaos Kitten better. Whether it's fixing a typo or implementing a complex attack chain, we appreciate your help!

Questions? Open an issue or start a discussion. We're happy to help! 🐱

---

<p align="center">
  <em>"Breaking your code before hackers do"</em>
</p>
