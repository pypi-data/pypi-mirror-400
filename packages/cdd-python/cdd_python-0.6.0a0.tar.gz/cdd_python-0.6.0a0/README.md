# CDD Framework - Python Adapter (0.6.0a0)

> **Official Python adapter for the CDD (Cyberattack-Driven Development) framework.**
> Effortlessly audit your application's security posture using our high-performance native Rust core.

The Cloud Detection & Defense (CDD) Python adapter allows you to integrate automated security audits into your Python projects. 

It wraps the high-performance **Ratel Core** (Rust) into a developer-friendly Python package.

## Installation

Install the adapter via pip (ensure you have access to your private/public registry):

```bash
pip install cdd-python
```

## How it Works
This adapter follows the "Binary Pivot" architecture:

Zero-Config Extraction: At runtime, the library detects your OS (Windows, Linux, macOS) and extracts the embedded ratel binary to ~/.ratel/bin/.

Pythonic Standards: It automatically detects Python project structures (presence of requirements.txt or pyproject.toml) to place security scenarios in tests/security/.

Process Isolation: The audit runs as a native subprocess, keeping your Python environment fast and clean.

## Usage
### 1. Initialization
Run this once to bootstrap your project with an expert security scenario.

```
Python

import cdd

# Generates tests/security/security.ratel
cdd.init() 
```


### 2. Configuration (Ratel DSL)
The security logic is defined in the .ratel file. This allows you to update security rules without touching your Python code.

File: tests/security/security.ratel

```
Code snippet

SCENARIO "Python API Security Audit"
TARGET "http://localhost:8000"

WITH SCOPE KERNEL
WITH SCOPE TERRITORY

IGNORE "FAVICON_FINGERPRINT"
```

### 3. Execution
Integrate the audit into your development workflow or CI/CD scripts.

```Python

import cdd

if __name__ == "__main__":
    print("Starting Security Audit...")
    
    # Executes the embedded Ratel binary using the .ratel file
    cdd.run()

```

## Integration with Pytest
You can easily wrap the audit in a pytest suite:


```Python

def test_security_compliance():
    import cdd
    # CDD will raise a CalledProcessError if the audit fails
    cdd.run()
```


## Update the package

Update the setup.py

```
rm -rf dist/ build/ *.egg-info
python -m build
python -m twine upload dist/*
```


Part of the CDD-Framework organization.