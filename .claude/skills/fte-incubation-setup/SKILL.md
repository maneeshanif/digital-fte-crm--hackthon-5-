---
name: fte-incubation-setup
description: Set up development environment for Digital FTE incubation phase. Use when starting Phase 1 work or initializing a new FTE prototype project.
---

# FTE Incubation Setup

Set up complete development environment for building Digital FTE prototypes.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing project structure, any prior setup files, .env configurations |
| **Conversation** | User's OS/platform, preferred Python version, existing tools (uv, poetry, pip) |
| **Skill References** | Package requirements, directory structure patterns |
| **User Guidelines** | Project naming conventions, virtual environment preferences |

## Setup Process

### 1. Initialize Python Project

Create a new Python project with uv:

```bash
# Initialize project
uv init <project-name>
cd <project-name>

# Verify Python version (3.10+ recommended)
uv run python --version
```

### 2. Create Directory Structure

```bash
# Create required directories
mkdir -p context src/agent src/channels src/mcp tests specs web-form
```

**Directory Purpose:**
- `context/` - Knowledge base files (company profile, product docs, etc.)
- `src/agent/` - Agent implementation files
- `src/channels/` - Channel-specific adapters (email, WhatsApp, web)
- `src/mcp/` - MCP server implementation
- `tests/` - Test files
- `specs/` - Specifications and discovery logs
- `web-form/` - Next.js web form prototype

### 3. Install Dependencies

```bash
# Core dependencies for FTE incubation
uv add fastmcp openai anthropic psycopg2-binary python-dotenv

# Development dependencies
uv add --dev pytest pytest-asyncio black mypy
```

**Dependency Rationale:**
- `fastmcp` - MCP server framework for tool exposure
- `openai` - OpenAI API for production agents (prototype uses anthropic)
- `anthropic` - Claude API for prototype development
- `psycopg2-binary` - PostgreSQL driver for database integration
- `python-dotenv` - Environment variable management

### 4. Create Configuration Files

#### `.env` Template

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# APIs
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# MCP
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# Channels
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
```

#### `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
logs/
```

### 5. Verify Setup

```bash
# Test Python environment
uv run python -c "import fastmcp; import anthropic; print('Setup successful')"

# Verify directory structure
ls -la context src/agent src/channels src/mcp tests specs web-form
```

## Troubleshooting

### uv not installed
```bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### PostgreSQL connection issues
- Ensure `psycopg2-binary` is installed (not `psycopg2`)
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`
- For Neon DB: Use connection string from Neon console

### MCP server issues
- Verify `fastmcp` version: `uv run python -c "import fastmcp; print(fastmcp.__version__)"`
- Check port availability: `netstat -an | grep <port>` (Linux/mac) or `netstat -an | findstr <port>` (Windows)

## Available Scripts

This skill includes automated scripts to speed up setup:

### setup_project.sh (Linux/mac)
Automated project initialization script that:
- Installs uv if not present
- Initializes Python project
- Creates directory structure
- Installs all dependencies
- Creates .env and .gitignore files
- Verifies setup

**Usage:**
```bash
./setup_project.sh <project-name>
```

### setup_project.ps1 (Windows)
Windows PowerShell version of the setup script with same functionality.

**Usage:**
```powershell
.\setup_project.ps1 -ProjectName <project-name>
```

### scripts/ directory structure
```
fte-incubation-setup/
├── SKILL.md                          # Main skill documentation
├── scripts/
│   ├── setup_project.sh                # Linux/mac automated setup
│   └── setup_project.ps1              # Windows automated setup
└── references/
    └── package-list.md                 # Complete package reference
```

## Next Steps

After setup:
1. Create context files using `fte-context-generator` skill
2. Build agent prototype using `fte-prototype-agent` skill
3. Create MCP server using `fte-mcp-server` skill
