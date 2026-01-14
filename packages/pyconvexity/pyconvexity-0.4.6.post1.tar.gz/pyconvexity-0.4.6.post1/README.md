# pyconvexity

Python library for energy system modeling and optimization with PyPSA.

[![PyPI version](https://badge.fury.io/py/pyconvexity.svg)](https://badge.fury.io/py/pyconvexity)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

pyconvexity is the Python library that powers [Convexity](https://bayesian.energy/convexity), providing programmatic access to energy system modeling and optimization. It stores models in SQLite databases and integrates with PyPSA for solving.

## Installation

```bash
pip install pyconvexity
```

With optional dependencies:

```bash
pip install pyconvexity[pypsa]     # PyPSA solver integration
pip install pyconvexity[excel]     # Excel import/export
pip install pyconvexity[all]       # All optional dependencies
```

## Quick Start

```python
import pyconvexity as px

# Create a new model database
px.create_database_with_schema("my_model.db")

# Create a network
with px.database_context("my_model.db") as conn:
    network_req = px.CreateNetworkRequest(
        name="My Network",
        start_time="2024-01-01 00:00:00",
        end_time="2024-01-01 23:00:00",
        time_resolution="PT1H",
    )
    px.create_network(conn, network_req)
    
    # Create components
    carrier_id = px.create_carrier(conn, name="AC")
    bus_id = px.create_component(conn, "BUS", "Main Bus", carrier_id=carrier_id)
    
    conn.commit()

# Solve the network
result = px.solve_network("my_model.db", solver_name="highs")
print(f"Success: {result['success']}, Objective: {result['objective_value']}")
```

## Documentation

Full documentation is available at: **[docs.bayesian.energy](https://docs.bayesian.energy/convexity/user-guide/advanced-features/pyconvexity/)**

- [API Reference](https://docs.bayesian.energy/convexity/user-guide/advanced-features/pyconvexity/api/api-reference)
- [Examples & Tutorials](https://docs.bayesian.energy/convexity/user-guide/advanced-features/pyconvexity/examples/example-1/)

## Development

### Setup

```bash
git clone https://github.com/bayesian-energy/pyconvexity.git
cd pyconvexity
pip install -e ".[dev,all]"
```

### Running Tests

```bash
pytest
```

### Documentation Deployment

API documentation is auto-generated and synced to [bayesian-docs](https://github.com/bayesian-energy/bayesian-docs).

**Generate API docs locally:**

```bash
python scripts/generate_api_docs.py --output-dir api-docs
```

**How it works:**
1. On push to `main` or release, the `sync-docs.yml` workflow runs
2. It generates API markdown from Python docstrings
3. Commits the generated docs to the `bayesian-docs` repository

**Setup for maintainers:**
- Add `DOCS_DEPLOY_TOKEN` secret to the repo (personal access token with `repo` scope for bayesian-docs)

## License

MIT License - see [LICENSE](LICENSE) for details.

