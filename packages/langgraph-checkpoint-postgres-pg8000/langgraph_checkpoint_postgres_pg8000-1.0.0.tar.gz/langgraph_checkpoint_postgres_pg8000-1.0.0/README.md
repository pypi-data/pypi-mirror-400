# LangGraph Checkpoint Postgres (pg8000)

[![PyPI](https://img.shields.io/pypi/v/langgraph-checkpoint-postgres-pg8000)](https://pypi.org/project/langgraph-checkpoint-postgres-pg8000/)
[![Python Versions](https://img.shields.io/pypi/pyversions/langgraph-checkpoint-postgres-pg8000.svg)](https://pypi.org/project/langgraph-checkpoint-postgres-pg8000/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A PostgreSQL checkpointer implementation for [LangGraph](https://github.com/langchain-ai/langgraph) using the [pg8000](https://codeberg.org/tlocke/pg8000) database driver.

## Why is this library needed?

The official [langgraph-checkpoint-postgres](https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint-postgres) library requires the [psycopg](https://www.psycopg.org/psycopg3/) database driver. However, certain deployment environments, particularly those using **Google Cloud SQL for PostgreSQL** with the [cloud-sql-python-connector](https://github.com/GoogleCloudPlatform/cloud-sql-python-connector)—**do not currently support psycopg**.

**This library serves as a stopgap solution** until the Google Cloud SQL Python Connector adds full psycopg support (expected early 2026). It provides the same checkpoint functionality as the official library but uses the `pg8000` driver, which is supported by the Cloud SQL Connector.

## Installation

```bash
# pip
pip install langgraph-checkpoint-postgres-pg8000
# uv
uv add langgraph-checkpoint-postgres-pg8000
# Poetry
poetry add langgraph-checkpoint-postgres-pg8000
```

## Usage

### Basic Setup

```python
from langgraph_checkpoint_postgres_pg8000 import Pg8000Saver
from sqlalchemy import create_engine

# Create SQLAlchemy engine
engine = create_engine("postgresql+pg8000://user:password@host/database")

# Initialize checkpointer
checkpointer = Pg8000Saver(engine=engine)

# Use with LangGraph
graph = graph_builder.compile(checkpointer=checkpointer)
```

**Note:** Consider using [sqlmodel-gcp-postgres](https://pypi.org/project/sqlmodel-gcp-postgres/) to create an SQLAlchemy/SQLModel compatible database engine that may be used with Google Cloud SQL deployments!


## Important Notes

> [!IMPORTANT]
> This library is nearly 100% based on the official `langgraph-checkpoint-postgres` implementation, with adaptations for `pg8000` instead of `psycopg`. The core logic and SQL queries remain the same.

> [!NOTE]
> Once the Google Cloud SQL Python Connector adds full psycopg support (expected early 2026), you should migrate to the official `langgraph-checkpoint-postgres` library for long-term support and updates.

## Related Projects

- [LangGraph](https://github.com/langchain-ai/langgraph) - Build stateful, multi-actor applications with LLMs
- [langgraph-checkpoint-postgres](https://github.com/langchain-ai/langgraph/tree/main/libs/checkpoint-postgres) - Official LangGraph PostgreSQL checkpointer using psycopg
- [cloud-sql-python-connector](https://github.com/GoogleCloudPlatform/cloud-sql-python-connector) - Python connector for Google Cloud SQL
- [sqlmodel-gcp-postgres](https://pypi.org/project/sqlmodel-gcp-postgres/) - SQLModel integration for Google Cloud SQL PostgreSQL

## License

MIT License - see [LICENSE](LICENSE) file for details.
