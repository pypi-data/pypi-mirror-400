![License](https://img.shields.io/badge/license-MIT-orange.svg) 
![OS](https://img.shields.io/badge/os-cross--platform-orange) 
![Library Python](https://img.shields.io/badge/python_library-3.8%2B-blue.svg) 
![Module Python](https://img.shields.io/badge/python_modules-3.5%2B-green.svg) 

# MultiEnvEmployer

**MultiEnvEmployer** — a Python library for calling functions and generators from modules in **other virtual environments**, including environments with **different Python versions** and **conflicting dependencies**.

The library is designed for situations where code **cannot be imported directly** but needs to be called and controlled from a single main process.

---

## Key Features

* run Python code in **isolated virtualenvs**
* support for **different Python versions**
* call functions as regular Python functions
* pass data between processes
* support for `return`, `yield`, and streaming large data
* intercept `print()` without breaking IPC
* execution time control (timeouts)
* error handling as regular exceptions
* file caching of results

---

## Quick Start

```python
from MultiEnvEmployer import Employer, RemoteModule

emp = Employer(
    project_dir="/path/to/project",
    venv_path="/path/to/venv"
)

moduleA = RemoteModule(emp, "moduleA")

result = moduleA.add(2, 4)
print(result)
```

The `moduleA.py` module should be located in the specified project directory and will be executed **in a different virtualenv**.

---

## How It Works

* code runs in a separate Python process
* the specified virtualenv is used
* data is exchanged through a binary channel (`pickle`)
* errors and `print()` are correctly proxied to the main process

From the user's perspective, calls look like regular Python code.

---

## Data Return

Supported:

* regular `return`
* generators (`yield`)
* streaming large data (automatic)

For large objects, data is sent in chunks to avoid memory overload.

---

## Timeouts

Supported modes:

* unlimited
* hard timeout
* inactivity-based timeout (`progress`)

If the time limit is exceeded, the worker process will be terminated.

---

## Error Handling

Errors inside the remote code are raised as Python exceptions:

* `RemoteExecutionError`
* `RemoteTimeoutError`
* `RemoteImportError`
* and others

---

## Who This Library Is For

MultiEnvEmployer is useful if you need to:

* run code with conflicting dependencies
* support multiple Python versions
* avoid using import due to architectural constraints
* control code execution at runtime

This is **not a dev tool**, but an execution infrastructure layer.

---

## Documentation and Source Code

Full documentation, architecture, and examples are available on GitHub:

**[https://github.com/REYIL/MultiEnvEmployer](https://github.com/REYIL/MultiEnvEmployer)**

---

## License

MIT License
