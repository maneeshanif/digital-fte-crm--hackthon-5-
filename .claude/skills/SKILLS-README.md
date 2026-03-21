# FTE Incubation Skills

Complete skills package for Digital FTE Phase 1 Incubation work.

## Skills Overview

All 5 skills created in `.claude/skills/` directory with scripts, references, and assets.

### 1. fte-incubation-setup (24KB)

**Purpose:** Set up development environment for Digital FTE incubation phase

**Files:**
- `SKILL.md` - Main skill documentation with setup instructions
- `scripts/setup_project.sh` - Linux/mac automated setup script
- `scripts/setup_project.ps1` - Windows PowerShell setup script
- `references/package-list.md` - Complete package reference

**What It Does:**
- Initializes Python project with uv
- Creates directory structure (context, src/agent, src/channels, src/mcp, tests, specs, web-form)
- Installs all dependencies (fastmcp, openai, anthropic, psycopg2-binary, python-dotenv, pytest, black, mypy)
- Creates .env template and .gitignore
- Verifies setup is successful

---

### 2. fte-context-generator (28KB)

**Purpose:** Generate all context files for Digital FTE prototypes

**Files:**
- `SKILL.md` - Main skill documentation with context file specifications
- `scripts/generate_context.py` - Interactive Python script
- `assets/company-profile-template.md` - Manual template
- `references/context-file-specs.md` - Detailed specifications

**What It Does:**
- Prompts for company information interactively
- Creates 5 context files:
  - `context/company-profile.md`
  - `context/product-docs.md`
  - `context/sample-tickets.json`
  - `context/escalation-rules.md`
  - `context/brand-voice.md`
- Provides validation and best practices

---

### 3. fte-prototype-agent (56KB)

**Purpose:** Build core customer agent prototype with sentiment analysis, knowledge base search, and response generation

**Files:**
- `SKILL.md` - Main skill documentation with agent architecture
- `scripts/scaffold_agent.py` - Automated agent scaffolding script
- `assets/agent-template.py` - Customizable agent template
- `references/agent-architecture.md` - Complete architecture reference

**What It Does:**
- Creates complete agent file structure
- Implements all core methods:
  - `process_message()` - Main entry point
  - `analyze_sentiment()` - Sentiment detection
  - `determine_priority()` - Priority classification
  - `search_knowledge_base()` - KB search
  - `generate_response()` - Response generation
  - `check_escalation()` - Escalation logic
  - `detect_category()` - Category detection
  - `store_conversation()` - Memory management
  - `get_customer_history()` - History retrieval
- Creates test suite with pytest fixtures
- Implements channel-specific formatting (email, WhatsApp, web_form)

---

### 4. fte-mcp-server (44KB)

**Purpose:** Create FastMCP server with 7 tools for FTE capabilities

**Files:**
- `SKILL.md` - Main skill documentation with MCP tool specifications
- `scripts/scaffold_mcp_server.py` - Automated MCP server scaffolding
- `assets/server-config.json` - Server configuration template
- `references/mcp-tools-reference.md` - Complete tool specifications

**What It Does:**
- Creates FastMCP server instance
- Implements all 7 MCP tools:
  1. `search_knowledge_base` - Search product documentation
  2. `create_ticket` - Create support ticket
  3. `get_customer_history` - Get cross-channel history
  4. `send_response` - Send response via channel
  5. `escalate_to_human` - Escalate to human support
  6. `analyze_sentiment` - Analyze message sentiment
  7. `get_channel_formatting` - Get channel guidelines
- Creates tool descriptions with parameters and return types
- Implements proper JSON response formats
- Creates test suite for MCP server

---

### 5. fte-testing-validator (40KB)

**Purpose:** Test and validate FTE prototype with performance metrics and edge case coverage

**Files:**
- `SKILL.md` - Main skill documentation with testing criteria
- `scripts/run_tests.py` - Comprehensive test runner
- `references/test-coverage-baseline.md` - Coverage and performance targets

**What It Does:**
- Runs all test suites sequentially:
  - Agent functional tests
  - MCP server tests
  - Edge case tests
  - Performance tests
  - All tests with coverage
- Captures test results and timings
- Generates HTML validation report (`tests/validation_report.md`)
- Creates JSON results for programmatic access (`tests/validation_results.json`)
- Calculates success rate and coverage metrics
- Compares against performance baselines
- Provides pass/fail assessment

---

## Skill Directory Structure

Each skill follows consistent structure:

```
skill-name/
├── SKILL.md                          # Main skill documentation
├── scripts/                            # Executable automation scripts
│   ├── script1.py
│   └── script2.sh
├── assets/                             # Templates and boilerplate
│   ├── template1.md
│   └── config.json
└── references/                          # Domain knowledge and specs
    ├── reference1.md
    └── specs.md
```

## Total Skills Package

| Metric | Count | Size |
|---------|--------|-------|
| Total Skills | 5 | 192KB |
| Scripts | 6 | - |
| References | 5 | - |
| Assets | 3 | - |
| Total Files | 19 | - |

## Usage Workflow

### Phase 1: Setup
```
1. Use fte-incubation-setup skill
   → Run: ./setup_project.sh <project-name>
   → Result: Complete project structure ready
```

### Phase 2: Context Generation
```
2. Use fte-context-generator skill
   → Run: python scripts/generate_context.py
   → Result: All 5 context files created
```

### Phase 3: Agent Implementation
```
3. Use fte-prototype-agent skill
   → Run: python scripts/scaffold_agent.py
   → Result: Working agent with all methods
```

### Phase 4: MCP Server
```
4. Use fte-mcp-server skill
   → Run: python scripts/scaffold_mcp_server.py
   → Result: MCP server with 7 tools
```

### Phase 5: Testing & Validation
```
5. Use fte-testing-validator skill
   → Run: python scripts/run_tests.py
   → Result: Validation report with metrics
```

## Skill Activation

These skills will be automatically available to Claude Code when:
- Located in `.claude/skills/` directory
- Follow naming convention (lowercase, hyphens, ≤64 chars)
- Have valid SKILL.md frontmatter

## Quick Start

```bash
# 1. Navigate to project
cd your-project-directory

# 2. Ask Claude to use a skill
# Example: "Use fte-incubation-setup to set up the project"

# 3. Claude will execute the skill
# Skills include automated scripts for faster execution
```

## Maintenance

### Updating Skills
To update any skill:
1. Edit `SKILL.md` for documentation changes
2. Update `scripts/` for automation changes
3. Add new files to `references/` or `assets/` as needed
4. Skills will be automatically available next session

### Adding New Skills
To add a new skill:
1. Create directory: `.claude/skills/new-skill-name/`
2. Create `SKILL.md` with proper frontmatter
3. Add `scripts/`, `assets/`, `references/` as needed
4. Follow skill-creator-pro guidelines

## References

- **skill-creator-pro**: Guidelines for creating production-grade skills
- **skill-validator**: Validation criteria for skill quality
- **part-1.md**: Phase 1 Incubation requirements
- **README.md**: Main project documentation

---

**Created:** 2024-03-14
**Status:** Production Ready
**Version:** 1.0.0
