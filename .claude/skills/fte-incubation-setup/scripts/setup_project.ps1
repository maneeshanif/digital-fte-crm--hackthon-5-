# Setup FTE Incubation Project for Windows
# Automated project initialization script

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectName
)

Write-Host "=== FTE Incubation Project Setup ===" -ForegroundColor Green

# Check if uv is installed
Write-Host "Step 1: Checking uv installation..." -ForegroundColor Green
$uvExists = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvExists) {
    Write-Host "uv not found. Installing..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
}

# Initialize project
Write-Host "Step 2: Initialize Python project with uv..." -ForegroundColor Green
uv init $ProjectName
Set-Location $ProjectName

# Create directory structure
Write-Host "Step 3: Create directory structure..." -ForegroundColor Green
$directories = @(
    "context",
    "src\agent",
    "src\channels",
    "src\mcp",
    "tests",
    "specs",
    "web-form"
)
foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Install dependencies
Write-Host "Step 4: Install dependencies..." -ForegroundColor Green
uv add fastmcp openai anthropic psycopg2-binary python-dotenv
uv add --dev pytest pytest-asyncio black mypy

# Create .env template
Write-Host "Step 5: Create configuration files..." -ForegroundColor Green
@"
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
"@ | Out-File -FilePath .env -Encoding UTF8

# Create .gitignore
@"
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
"@ | Out-File -FilePath .gitignore -Encoding UTF8

# Create placeholder files
Write-Host "Step 6: Create placeholder files..." -ForegroundColor Green
New-Item -ItemType File -Force -Path "context\.gitkeep"
New-Item -ItemType File -Force -Path "src\agent\__init__.py"
New-Item -ItemType File -Force -Path "src\channels\__init__.py"
New-Item -ItemType File -Force -Path "src\mcp\__init__.py"
New-Item -ItemType File -Force -Path "tests\__init__.py"

# Verify setup
Write-Host "Step 7: Verify setup..." -ForegroundColor Green
uv run python --version
uv run python -c "import fastmcp; import anthropic; print('✅ Dependencies installed successfully')"

Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Use 'fte-context-generator' skill to create context files"
Write-Host "  2. Use 'fte-prototype-agent' skill to build the agent"
Write-Host "  3. Use 'fte-mcp-server' skill to create MCP server"
