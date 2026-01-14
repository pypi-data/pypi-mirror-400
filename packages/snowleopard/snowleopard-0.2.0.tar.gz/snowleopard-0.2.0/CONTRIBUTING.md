# Contributing

Thanks for your interest in contributing to the Snow Leopard Python SDK!

Questions? Reach out on [Discord](https://discord.gg/WGAyr8NpEX)

## Getting Started

### Prerequisites

- Python 3.11 (our default dev version)
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

0. **Fork this repository**
   If you are unfamiliar contributing to open source projects, see [first-contributions](https://github.com/firstcontributions/first-contributions) for a great walkthrough.

1. **Clone your fork**
   ```bash
   git clone https://github.com/SnowLeopard-AI/snowleopard_py.git
   cd snowleopard_py
   ```

2. **Install dependencies**
   ```bash
   uv sync --dev
   ```

3. **Running tests**
   ```bash
   uv run pytest
   ```

### Testing with Different Python Versions

To test against a specific Python version:
```bash
uv run --python 3.10 pytest
```


### Re-Recording Cassettes or Writing New Tests

Tests use cassettes to be able to easily mock snowleopard network traffic. No configuration is needed when re-running 
tests, but to re-record or author new tests a .env file is needed in tests.

```bash
touch tests/.env
```

```.dotenv
#SNOWLEOPARD_LOC=
#SUPERHEROES_DFID=
#SNOWLEOPARD_API_KEY=
SNOWLEOPARD_TEST_RECORD_MODE=once
```
See [pyvcr docs](https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes) for more information on recording 
modes. Once will re-record only if the file is missing, so to re-record you must delete it first.

