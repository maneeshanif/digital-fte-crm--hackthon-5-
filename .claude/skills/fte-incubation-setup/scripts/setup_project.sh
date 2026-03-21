#!/bin/bash
# Setup FTE Incubation Project
# Automated project initialization script

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== FTE Incubation Project Setup ===${NC}"

# Check if project name provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: ./setup_project.sh <project-name>${NC}"
    exit 1
fi

PROJECT_NAME=$1

echo -e "${GREEN}Step 1: Initialize Python project with uv...${NC}"
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
fi

uv init "$PROJECT_NAME"
cd "$PROJECT_NAME"

echo -e "${GREEN}Step 2: Create directory structure...${NC}"
mkdir -p context src/agent src/channels src/mcp tests specs web-form

echo -e "${GREEN}Step 3: Install dependencies...${NC}"
uv add fastmcp openai anthropic psycopg2-binary python-dotenv
uv add --dev pytest pytest-asyncio black mypy

echo -e "${GREEN}Step 4: Create configuration files...${NC}"

# .env template
cat > .env << 'EOF'
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
EOF

# .gitignore
cat > .gitignore << 'EOF'
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
EOF

# pyproject.toml - add script section
echo -e "${GREEN}Step 5: Add convenience scripts to pyproject.toml...${NC}"
# pyproject.toml already created by uv, we add to it

echo -e "${GREEN}Step 6: Verify setup...${NC}"
uv run python --version
uv run python -c "import fastmcp; import anthropic; print('✅ Dependencies installed successfully')"

echo -e "${GREEN}Step 7: Create placeholder files...${NC}"
touch context/.gitkeep
touch src/agent/__init__.py
touch src/channels/__init__.py
touch src/mcp/__init__.py
touch tests/__init__.py

echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Next steps:"
echo "  1. cd $PROJECT_NAME"
echo "  2. Use 'fte-context-generator' skill to create context files"
echo "  3. Use 'fte-prototype-agent' skill to build the agent"
echo "  4. Use 'fte-mcp-server' skill to create MCP server"
