# cdis_oauth2client

A Python module providing a Flask blueprint and associated functions for CTDS
microservices such as gdcapi.

## Requirements

- Python **>= 3.13**
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

Add this library to your project with:

    poetry add cdis_oauth2client

## Usage

```python
from flask import Flask
import cdis_oauth2client

app = Flask(__name__)
app.register_blueprint(cdis_oauth2client.blueprint)
```

## Development

To start development of this library, run:

    poetry install --with dev
