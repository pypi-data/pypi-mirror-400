# bcrypt-speed-tests

Small CLI for benchmarking bcrypt cost factors (rounds) so you can pick a
sensible value
on your target hardware.

## What it does

- Hashes a fixed password multiple times per cost factor.
- Reports average time per cost in milliseconds.
- Runs locally on the same machine your app will use.

## Requirements

- Python 3.9+
- `bcrypt` (installed via project dependencies)

## Install & Run from PyPI

Install uv first: <https://docs.astral.sh/uv/>

Preferred install with uv as a global tool:

```bash
uv tool install bcrypt-speed-tests
```

Run directly without installing:

```bash
uvx bcrypt-speed-tests
```

Add it to an existing project as a development dependency:

```bash
uv add bcrypt_speed_tests
```

Alternative installs:

```bash
pipx install bcrypt-speed-tests
```

```bash
pip install bcrypt-speed-tests
```

## Install from repo

Clone and install locally:

```bash
git clone https://github.com/seapagan/bcrypt-speed-tests.git
cd bcrypt-speed-tests
uv sync
```

`uv sync` creates a local `.venv` by default.

### Activate the virtual environment

```bash
source .venv/bin/activate
```

Deactivate when done:

```bash
deactivate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Or with pip:

```bash
pip install -e .
```

## Run

```bash
bcrypt-speed-tests
```

### CLI options

Available options:

```text
Usage: bcrypt-speed-tests [OPTIONS] COMMAND [ARGS]...

Run the benchmark and print a timing table.

Options:
  --iterations  -i  INTEGER RANGE [x>=1]      Hashes to run per cost factor.
                                              [default: 3]
  --cost        -c  INTEGER RANGE [4<=x<=31]  Cost factor(s)/rounds. Repeat to
                                              pass multiple values.
  --help                                     Show this message and exit.
```

Override defaults at runtime:

```bash
bcrypt-speed-tests --iterations 5 --cost 10 --cost 12 --cost 14
```

## Tasks

Run via poethepoet:

```bash
poe ruff
poe mypy
poe format
```

## Configure

Edit defaults in `src/bcrypt_speed_tests/benchmark.py`:

- `ITERATIONS`: hashes per cost factor
- `COSTS`: bcrypt rounds (cost factor) range
- `PASSWORD`: fixed input

## Example output

```pre
Iterations per cost: 3

Cost | Avg time (ms)
----------------------
  10 |        23.4
  11 |        46.8
  12 |        93.1
  13 |       185.7
  14 |       370.9
```

## License

MIT
