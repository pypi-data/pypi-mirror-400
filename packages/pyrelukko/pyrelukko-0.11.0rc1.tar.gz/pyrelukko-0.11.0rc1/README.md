# PyRelukko

![PyPI - Version](https://img.shields.io/pypi/v/pyrelukko.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyrelukko.svg)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fgitlab.com%2Frelukko%2Fpyrelukko%2F-%2Fraw%2Fmaster%2Fpyproject.toml%3Fref_type%3Dheads)
![Gitlab Pipeline Status](https://img.shields.io/gitlab/pipeline-status/relukko%2Fpyrelukko?branch=master)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pyrelukko)
![PyPI - License](https://img.shields.io/pypi/l/pyrelukko)
![GitLab License](https://img.shields.io/gitlab/license/relukko%2Fpyrelukko)
![PyPI - Format](https://img.shields.io/pypi/format/pyrelukko)
![PyPI - Status](https://img.shields.io/pypi/status/pyrelukko)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/pyrelukko)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/pyrelukko)
![GitLab Stars](https://img.shields.io/gitlab/stars/relukko%2Fpyrelukko)
![GitLab Forks](https://img.shields.io/gitlab/forks/relukko%2Fpyrelukko)

---

**PyRelukko** is the official Python client library for the
[Relukko](https://gitlab.com/relukko/relukko) resource-locking backend. It
provides a simple, distributed locking mechanism for coordinating access to
shared resources across multiple Python processes or services.

Relukko is intentionally lightweight: it is designed for **collaborative
environments**. The system assumes clients behave cooperatively, and by design
it does **not** enforce protection against misbehaving clients.

## Documentation

Full API documentation can be found at:

👉 [https://pyrelukko.readthedocs.io](https://pyrelukko.readthedocs.io)

---

## Features

* **Simple, Pythonic API** for acquiring and releasing locks.
* **Centralized lock management** via the
  [Relukko](https://gitlab.com/relukko/relukko) backend.
* **Lightweight and dependency-minimal**.
* **Useful for distributed systems, CI pipelines,
  automated testing and shared-resource orchestration**.

---

## Important Design Note

Relukko and PyRelukko are built for *trusted*, *collaborative* clients.

### ⚠️ No client-side trust guarantees

A client that connects to the Relukko backend **can forcibly release any
lock**, including those owned by another client. There is **no protection**
against malicious manipulation of locks.

This is an intentional design decision to keep the system simple and
lightweight.

If you require secure, adversarial-resistant locking, you should consider using
a system built upon consensus algorithms (e.g., etcd, Consul, Zookeeper).

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

👉 [https://pyrelukko.readthedocs.io](https://pyrelukko.readthedocs.io)

### 3. **Robotframework-Relukko (Python)**

Robot Framework keyword library that enables acquiring and releasing locks
directly from Robot Framework test suites.
Depends on **PyRelukko**.

Repository: [https://gitlab.com/relukko/robotframework-relukko](https://gitlab.com/relukko/robotframework-relukko)

---

## Installation

Install via pip:

```bash
pip install pyrelukko
```

Requires Python **3.11+**.

---

## Quick Start

### Basic Example

```python
from pyrelukko import RelukkoClient


relukko = RelukkoClient(
    base_url="http://localhost:3000",
    api_key="api-key",
)

lock = relukko.acquire_relukko("LockName", "Creator", 300)
lock_id = lock.get('id')

# Perform work while holding the lock

relukko.delete_relukko(lock_id)
```

---

## When to Use PyRelukko

PyRelukko is ideal for:

* Distributed test harnesses
* CI/CD job coordination
* Server orchestration scripts
* Managing exclusive access to hardware devices or simulation environments
* Any cooperative environment where multiple workers need a shared mutex

It is **not** designed for untrusted environments or where mutual exclusion
must be strongly enforced.

---

## Limitations

* ❗ **A malicious or buggy client can release locks it doesn’t own.**
* ❗ No cryptographic guarantees or client identity.
* ❗ Requires a running Relukko backend server.
* ❗ Not fault-tolerant like consensus-based systems.

These limitations are **intentional**, in exchange for simplicity and minimal
overhead.

---

## Running the Backend

The backend is written in Rust and provides a simple HTTP API.
See the backend repository for instructions:

👉 [https://gitlab.com/relukko/relukko](https://gitlab.com/relukko/relukko)

---

## Contributing

Contributions to both the Python client and Rust backend are welcome!  Feel
free to open issues or merge requests in the relevant GitLab repository.

---

## License

MIT License.
See `LICENSE` for details.
