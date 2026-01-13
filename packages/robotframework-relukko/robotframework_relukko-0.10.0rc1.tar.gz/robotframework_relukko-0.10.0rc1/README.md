# Robotframework Relukko

[![PyPI - Version](https://img.shields.io/pypi/v/robotframework-relukko.svg)](https://pypi.org/project/robotframework-relukko)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/robotframework-relukko.svg)](https://pypi.org/project/robotframework-relukko)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fgitlab.com%2Frelukko%2Frobotframework-relukko%2F-%2Fraw%2Fmaster%2Fpyproject.toml%3Fref_type%3Dheads)
![Gitlab Pipeline Status](https://img.shields.io/gitlab/pipeline-status/relukko%2Frobotframework-relukko?branch=master)
![PyPI - Downloads](https://img.shields.io/pypi/dm/robotframework-relukko)
![PyPI - License](https://img.shields.io/pypi/l/robotframework-relukko)
![GitLab License](https://img.shields.io/gitlab/license/relukko%2Frobotframework-relukko)
![PyPI - Format](https://img.shields.io/pypi/format/robotframework-relukko)
![PyPI - Status](https://img.shields.io/pypi/status/robotframework-relukko)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/robotframework-relukko)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/robotframework-relukko)
![GitLab Stars](https://img.shields.io/gitlab/stars/relukko%2Frobotframework-relukko)
![GitLab Forks](https://img.shields.io/gitlab/forks/relukko%2Frobotframework-relukko)
-----

See the keywords documentation
https://relukko.gitlab.io/robotframework-relukko/

```robot
*** Settings ***
Library    Relukko    creator=Creator Name


*** Test Cases ***
Test Resource Lock
    Set Up Relukko    http://localhost:3000    some-api-key
    Acquire Relukko    LockName    8m34s
    ${lock}    Keep Relukko Alive For The Next    6m
    Log    ${lock}
    ${lock}    Keep Relukko Alive For The Next "50" Seconds
    Log    ${lock}
    ${lock}    Keep Relukko Alive For The Next 5 Min
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time    7m
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time "60" Seconds
    Log    ${lock}
    ${lock}    Add To Current Relukko Expire At Time 5 Min
    Log    ${lock}
    ${lock}    Update Relukko    creator=Mark
    Log    ${lock}
    ${lock}    Update Relukko    expires_at=2025-01-01T12:34:56.123456Z
    Log    ${lock}
    ${lock}    Get Current Relukko
    Log    ${lock}
    ${expires_at}    Get Relukko Expires At Time
    Log    ${expires_at}
    ${created_at}    Get Relukko Created At Time
    Log    ${created_at}
    ${lock}    Get All Relukkos
    Log    ${lock}
    ${lock}    Delete Relukko
    Log    ${lock}
```

---

## Ecosystem

The Relukko ecosystem consists of the following components:

### 1. **Relukko Backend (Rust)**

The backend is responsible for storing and arbitrating lock states.

Repository: [https://gitlab.com/relukko/relukko](https://gitlab.com/relukko/relukko)

### 2. **PyRelukko Client (Python)**

This Python package communicates with the backend, providing user-friendly
locking primitives.

Repository: [https://gitlab.com/relukko/pyrelukko](https://gitlab.com/relukko/pyrelukko)

### 3. **Robotframework-Relukko (Python)**

Robot Framework keyword library that enables acquiring and releasing locks
directly from Robot Framework test suites.
Depends on **PyRelukko**.

Repository: [https://gitlab.com/relukko/robotframework-relukko](https://gitlab.com/relukko/robotframework-relukko)

