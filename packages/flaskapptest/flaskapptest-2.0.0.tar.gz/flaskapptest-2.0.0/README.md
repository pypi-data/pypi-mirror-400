# FlaskAppTest

[![PyPI](https://img.shields.io/pypi/v/flaskapptest)](https://pypi.org/project/flaskapptest)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

**FlaskAppTest** is a production-grade, AST-based Flask API testing CLI.  
It allows developers and QA engineers to **scan Flask projects**, detect endpoints, generate payloads, run interactive manual tests, execute batch tests, and integrate easily into **CI/CD pipelines**.

---

## Features

- ✅ Detect Flask applications automatically via AST analysis
- ✅ Extract Flask endpoints and their HTTP methods
- ✅ Generate request payload templates (path, query, body parameters)
- ✅ Run **interactive manual testing** (`manual` mode)
- ✅ Execute **batch testing** for all endpoints automatically (`batch` mode)
- ✅ CI/CD-friendly non-interactive tests with proper exit codes (`ci` mode)
- ✅ Response validation and structured test reports
- ✅ Compatible with Python 3.9+ and production-ready Flask projects

---

## Installation

```bash
pip install flaskapptest

Usage
CLI entry point
flaskapptest --help

1. Manual Mode (Interactive)
flaskapptest manual --project /path/to/flask/project --base-url http://127.0.0.1:5000


Prompts you to select endpoints and fill payloads interactively

Useful for exploratory testing

2. Batch Mode (Automatic)
flaskapptest batch --project /path/to/flask/project --fail-fast


Automatically runs all detected endpoints

Optional --fail-fast stops execution on first failure

3. CI/CD Mode (Non-interactive)
flaskapptest ci --project /path/to/flask/project --base-url http://127.0.0.1:5000


Designed for CI/CD pipelines

Exits with:

0 → all tests passed

1 → test failures detected

2 → configuration/runtime error

Example
# Interactive manual testing
flaskapptest manual --project ./my_flask_app

# Automatic batch testing
flaskapptest batch --project ./my_flask_app --fail-fast

# CI/CD non-interactive testing
flaskapptest ci --project ./my_flask_app

Acknowledgements

Built by Ganesh Nalawade

Inspired by automated API testing concepts and AST-based code analysis