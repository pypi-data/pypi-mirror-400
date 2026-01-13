# Beancount LSB Importer

[![image](https://img.shields.io/pypi/v/beancount-lsb.svg)](https://pypi.python.org/pypi/beancount-lsb)
[![image](https://img.shields.io/pypi/pyversions/beancount-lsb.svg)](https://pypi.python.org/pypi/beancount-lsb)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

`beancount-lsb` provides an importer for converting CSV exports of [LSB (Lån & Spar Bank)](https://www.lsb.dk) account summaries to the [Beancount](http://furius.ca/beancount/) format.

## Installation

```sh
$ pip install beancount-lsb
```

In case you prefer installing from the Github repository, please note that `main` is the development branch so `stable` is what you should be installing from.

## Usage

If you're not familiar with how to import external data into Beancount, please read [this guide](https://beancount.github.io/docs/importing_external_data.html) first.

### Beancount 3.x

Beancount 3.x has replaced the `config.py` file based workflow in favor of having a script based workflow, as per the [changes documented here](https://docs.google.com/document/d/1O42HgYQBQEna6YpobTqszSgTGnbRX7RdjmzR2xumfjs/edit#heading=h.hjzt0c6v8pfs). The `beangulp` examples suggest using a Python script based on `beangulp.Ingest`. Here's an example of how that might work:

Add an `import.py` script in your project root with the following contents:

```python
from beancount_lsb import LSBImporter
from beangulp import Ingest

importers = (
    LSBImporter(
        "Assets:LSB:Checking",
        "0400 4024493887",
        currency="DKK",
    ),
)

if __name__ == "__main__":
    ingest = Ingest(importers)
    ingest()
```

... and run it directly using `python import.py extract`.

### Beancount 2.x

Adjust your [config file](https://beancount.github.io/docs/importing_external_data.html#configuration) to include `LSBImporter`.

Add the following to your `config.py`:

```python
from beancount_lsb import LSBImporter

CONFIG = [
    LSBImporter(
        "Assets:LSB:Checking",
        "0400 4024493887",
        currency="DKK",
    ),
]
```

Once this is in place, you should be able to run `bean-extract` on the command line to extract the transactions and pipe all of them into your Beancount file.

```sh
$ bean-extract /path/to/config.py Posteringsdetaljer.csv >> you.beancount
```

## Contributing

Contributions are most welcome!

Please make sure you have Python 3.11+ and [uv](https://docs.astral.sh/uv/) installed.

1. Clone the repository: `git clone https://github.com/joandrsn/beancount-lsb`
2. Install the packages required for development: `uv sync --dev`
3. That's basically it. You should now be able to run the test suite: `uv run pytest`.