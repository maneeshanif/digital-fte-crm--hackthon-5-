# FTE Incubation Package Reference

Complete list of packages required for FTE prototype development.

## Core Dependencies

| Package | Version | Purpose |
|----------|---------|---------|
| fastmcp | Latest | MCP server framework for tool exposure |
| openai | Latest | OpenAI API for production agents |
| anthropic | Latest | Claude API for prototype development |
| psycopg2-binary | Latest | PostgreSQL driver for database |
| python-dotenv | Latest | Environment variable management |

## Development Dependencies

| Package | Version | Purpose |
|----------|---------|---------|
| pytest | Latest | Testing framework |
| pytest-asyncio | Latest | Async test support |
| black | Latest | Code formatting |
| mypy | Latest | Static type checking |

## Optional Dependencies (for Part 2)

| Package | Purpose |
|----------|---------|
| fastapi | REST API framework |
| uvicorn | ASGI server |
| alembic | Database migrations |
| sqlalchemy | ORM |
| kafka-python | Kafka client |
| redis | Caching |

## Installation Commands

```bash
# Core dependencies
uv add fastmcp openai anthropic psycopg2-binary python-dotenv

# Development dependencies
uv add --dev pytest pytest-asyncio black mypy

# For Part 2 (optional)
uv add fastapi uvicorn alembic sqlalchemy kafka-python redis
```

## Package Sources

- **uv Package Index**: https://pypi.org/
- **FastMCP Docs**: https://github.com/jlowin/fastmcp
- **OpenAI Docs**: https://platform.openai.com/docs
- **Anthropic Docs**: https://docs.anthropic.com/
