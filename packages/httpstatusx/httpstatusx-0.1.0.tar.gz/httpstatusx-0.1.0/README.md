[![PyPI version](https://badge.fury.io/py/httpstatusx.svg)](https://pypi.org/project/httpstatusx/)
[![CI](https://github.com/Adamkoda2306/httpstatusx/actions/workflows/ci.yml/badge.svg)](https://github.com/Adamkoda2306/httpstatusx/actions)
[![Python versions](https://img.shields.io/pypi/pyversions/httpstatusx)](https://pypi.org/project/httpstatusx/)

# httpstatusx 🚦

**httpstatusx** is a semantic, bidirectional, and framework-agnostic Python library for working with HTTP status codes.

It removes the need to memorize numeric HTTP codes and helps backend developers write clean, readable, and maintainable APIs.

---

## ✨ Features

- Full IANA HTTP status code coverage
- Name → Code and Code → Name lookup
- Semantic categories (success, client_error, server_error, etc.)
- Fuzzy matching for shorthand queries
- FastAPI & Flask integrations
- Command-line interface (CLI)
- Fully tested & open-source

---

## 📦 Installation

```bash
pip install httpstatusx
```

For development:
```bash
pip install -e .
```

---

## 🚀 Quick Start

```python
from httpstatusx import HTTP

HTTP["ok"]                 # 200
HTTP["created"]            # 201
HTTP["unauth"]             # 401
HTTP.name(404)             # "not_found"
HTTP.category(503)         # "server_error"
HTTP.is_error(400)         # True
```

---

## ⚡ Framework Integrations

### FastAPI

```python
from httpstatusx import fastapi

raise fastapi("not_found", "User not found")
```

### Flask

```python
from httpstatusx import flask

flask("unauthorized")
```

---

## 🖥️ CLI Usage

```bash
httpstatusx ok
httpstatusx 404
httpstatusx service_unavailable
```

---

## 🧪 Testing

```bash
pytest
pytest --cov=httpstatusx
```

---

## 📄 License

MIT License © 2025 Adam Koda