[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![PyPI](https://img.shields.io/pypi/v/lazyscribe-yaml)](https://pypi.org/project/lazyscribe-yaml/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lazyscribe-yaml)](https://pypi.org/project/lazyscrib-yaml/) [![codecov](https://codecov.io/gh/lazyscribe/lazyscribe-yaml/graph/badge.svg?token=W5TPK7GX7G)](https://codecov.io/gh/lazyscribe/lazyscribe-yaml)

# YAML-based artifact handling for lazyscribe

`lazyscribe-yaml` is a lightweight package that adds the following artifact handlers for `lazyscribe`:

* `yaml`

# Installation

Python 3.10 or above is required. Use `pip` to install:

```console
$ python -m pip install lazyscribe-yaml
```

# Usage

To use this library, simply log an artifact to a `lazyscribe` experiment or repository with `handler="yaml"`.

```python
from lazyscribe import Project

project = Project("project.json", mode="w")
with project.log("My experiment") as exp:
    exp.log_artifact(name="feature-names", value=["a", "b", "c"], handler="yaml")

project.save()
```
