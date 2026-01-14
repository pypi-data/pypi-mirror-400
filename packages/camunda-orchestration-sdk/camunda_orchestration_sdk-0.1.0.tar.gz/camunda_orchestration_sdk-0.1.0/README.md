## Camunda Orchestration Cluster API – Python SDK Generator

This project generates a Python SDK for the Camunda 8 Orchestration Cluster REST API from the OpenAPI specification.

### Overview

- Fetches the OpenAPI spec via shallow clone from the public repository (fallback to local checked-out repo if offline).
- Generates the SDK using OpenAPI Generator (prefers `npx`, falls back to Docker).
- Provides an extensible hooks system for post-processing tasks.

### Requirements

- Python 3.9+
- One of:
  - Node.js with `npx` available; or
  - Docker (for `openapitools/openapi-generator-cli`)

### Quick start

```bash
cd orchestration-cluster-api-python
# Install deps and run generation (defaults to output in ./generated)
make generate
```

Generated SDK will be placed in `generated/` by default. You can change this with `--out-dir`.

### Using the generated SDK

The generated SDK provides a `CamundaClient` class that wraps the underlying API client and provides a unified interface for both synchronous and asynchronous operations.

#### Initialization

```python
from camunda_orchestration_sdk import CamundaClient

# Unauthenticated (for local development)
client = CamundaClient(base_url="http://localhost:8080")

# Authenticated (for production/SaaS)
client = CamundaClient(
    base_url="https://...", 
    token="your-access-token"
)
```

#### Synchronous Usage

```python
with CamundaClient(base_url="http://localhost:8080") as client:
    topology = client.get_topology()
    print(topology)
```

#### Asynchronous Usage

```python
import asyncio
from camunda_orchestration_sdk import CamundaClient

async def main():
    async with CamundaClient(base_url="http://localhost:8080") as client:
        topology = await client.get_topology_async()
        print(topology)

asyncio.run(main())
```

### Logging

The SDK uses [loguru](https://github.com/Delgan/loguru) for logging. You can control the log level by setting the `LOGURU_LEVEL` environment variable.

```bash
# Run with INFO level (default is DEBUG)
LOGURU_LEVEL=INFO python your_script.py

# Run with WARNING level
LOGURU_LEVEL=WARNING python your_script.py

# Run with TRACE level (more verbose than DEBUG)
LOGURU_LEVEL=TRACE python your_script.py
```

### Local fallback of the spec

If the network is not available or the remote repository cannot be reached, the generator will use the locally cloned spec at:

- `../camunda-orchestration-cluster-api/specification/rest-api.yaml`

Ensure that repository is present in the workspace if you need offline generation.

### Configuration

`generator-config.yaml` holds OpenAPI Generator options such as package name. You may add or tweak options there.

You can also pass CLI arguments:

```bash
python3 generate.py \
  --out-dir ./generated \
  --generator python \
  --spec-ref main \
  --package-name camunda_orchestration_sdk
```

Run `python3 generate.py --help` for all options.

### Hooks (post-processing)

Add Python files under `hooks/` exporting a `run(context)` function. Hooks are executed in sorted order after generation.

`context` includes:

- `out_dir`: path to the generated SDK directory
- `spec_path`: path to the spec used for generation
- `config_path`: path to the generator config file
- `generator`: the generator type used (default `python`)

Example hook: see `hooks/postprocess_example.py`.

### Acceptance tests (post-generation)

After generation and post-processing, acceptance tests run automatically unless `--skip-tests` is provided. Tests live under `tests/acceptance/` and run against the generated package by injecting `PYTHONPATH`.

Run tests manually:

```bash
make test
```

### Integration tests (opt-in)

Integration tests live in `tests/integration` and require a running server. They are skipped unless `CAMUNDA_INTEGRATION=1` is set. By default, the client points to `http://localhost:8080/v2`; override with `CAMUNDA_BASE_URL`.

Run manually:

```bash
make itest
```

### Make targets

- `make generate` – run the generator (uses Python script)
- `make clean` – remove the `generated/` directory and cache

### License

Apache-2.0


