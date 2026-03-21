# Customer Success Digital FTE Specification

## Version
1.0.0 (Incubation Phase)

## Purpose
Automated customer success agent that handles customer inquiries across multiple channels with sentiment awareness and intelligent escalation.

## Architecture

### Layers
1. **Agent Layer** - Core customer agent with sentiment, priority, KB search, response generation
2. **MCP Layer** - FastMCP server exposing 7 tools
3. **Context Layer** - Knowledge base files (company profile, product docs, tickets, rules, brand voice)
4. **Testing Layer** - Unit tests for agent and MCP server

### Channels
- Email (Gmail integration)
- WhatsApp (Twilio integration - planned)
- Web Form (Next.js form - planned)

## Components

### 1. CustomerAgent Class
**Location:** `src/agent/customer_agent.py`

**Methods:**
- `process_message()` - Main entry point, orchestrates all processing steps
- `analyze_sentiment()` - Keyword-based sentiment detection (positive/neutral/negative)
- `determine_priority()` - Priority classification (low/medium/high/critical)
- `search_knowledge_base()` - Keyword overlap search of product docs
- `generate_response()` - Channel-specific response generation
- `check_escalation()` - Escalation decision logic
- `detect_category()` - Category classification (5 categories)
- `store_conversation()` - In-memory conversation storage
- `get_customer_history()` - Conversation history retrieval

### 2. MCP Server
**Location:** `src/mcp/server.py`

**Tools:**
1. `search_knowledge_base` - Search product documentation
2. `create_ticket` - Create support ticket
3. `get_customer_history` - Get cross-channel history
4. `send_response` - Send response via channel
5. `escalate_to_human` - Escalate to human support
6. `analyze_sentiment` - Analyze message sentiment
7. `get_channel_formatting` - Get channel guidelines

**Framework:** FastMCP
**Transport:** stdio
**Tool Count:** 7

### 3. Context Files
**Location:** `context/`

**Files:**
- `company-profile.md` - TechFlow SaaS company information
- `product-docs.md` - TechFlow features, use cases, troubleshooting, pricing
- `sample-tickets.json` - 50 example tickets across all channels
- `escalation-rules.md` - Escalation triggers and agent capabilities
- `brand-voice.md` - Channel-specific communication guidelines

## Data Flow

```
Customer Message
    ↓
Channel Detection
    ↓
Sentiment Analysis
    ↓
Priority Determination
    ↓
Knowledge Base Search
    ↓
Response Generation
    ↓
Escalation Check
    ↓
Store Conversation
    ↓
Return Response + Metadata
```

## Escalation Rules

**Always Escalate:**
1. Negative sentiment detected
2. Billing issues (refund, payment disputes, pricing)
3. Compliance/legal questions (HIPAA, GDPR, SOC2)
4. Critical priority issues
5. Feature requests

**Agent Handles:**
1. Product information questions
2. How-to guidance requests
3. Troubleshooting (non-urgent)
4. General support (account setup, basic integration)
5. Bug reports with workarounds

## Categories

1. **Technical** - Workflow, integration, API, bug, error, login
2. **Billing** - Refund, payment, price, invoice, billing
3. **Feature Request** - Feature, add, support, can you, would be great
4. **Compliance** - Security, HIPAA, GDPR, SOC2, compliance
5. **Pricing** - How much, cost, pricing, license, subscription

## Limitations (Phase 1)

### Prototype Limitations
- In-memory storage only (not persistent)
- Keyword-based sentiment (not ML)
- Keyword overlap search (not vector similarity)
- Template-based responses (not LLM-generated)
- No real channel integration (simulated)
- No external database (uses memory)
- No persistence across restarts
- No authentication/authorization

### Known Issues
1. Sentiment analysis accuracy limited to keyword matching
2. Knowledge base search may miss relevant info
3. Escalation logic is rule-based, not adaptive
4. No learning from past interactions
5. Limited context window (only current conversation)

## Part 2 Considerations

### Production Requirements
1. **Persistent Storage** - PostgreSQL database for customers, tickets, conversations
2. **ML-Based Sentiment** - Use Anthropic/OpenAI for more accurate analysis
3. **Vector Search** - Implement embedding-based similarity search for KB
4. **LLM Responses** - Generate responses using LLM instead of templates
5. **Real Channel Integration** - Gmail API, Twilio WhatsApp, Next.js web form
6. **Kafka Event Streaming** - Async processing of tickets and responses
7. **Repository Pattern** - Data access abstraction layer
8. **Services Layer** - Business logic separation from data access
9. **Worker Layer** - Background processing of tickets, responses, metrics
10. **Multi-File Agent** - Split agent into modules (agent.py, tools.py, prompts.py, etc.)

### Architecture Upgrades
- **8 Layers:** Agent, Worker, Services, Database, API, Kafka, Core, Channels, Frontend
- **Microservices:** Separate services for ticket processing, response dispatch, metrics collection
- **Event-Driven:** Kafka for async communication between services
- **REST API:** FastAPI for webhook endpoints
- **Database Migrations:** Alembic for schema management
- **Test Coverage:** 85%+ with pytest
- **CI/CD:** GitHub Actions for automated testing

## Success Criteria (Phase 1)

### Must Have
- [x] Working agent that processes messages across channels
- [x] Sentiment analysis (positive/neutral/negative)
- [x] Priority determination (low/medium/high/critical)
- [x] Knowledge base search functionality
- [x] Response generation with channel-specific formatting
- [x] Escalation logic following rules
- [x] MCP server with 7 tools
- [x] Context files for company, product, tickets, rules, voice
- [x] Test suite for agent functionality
- [x] Skills documentation

### Should Have
- [x] Test suite with 80%+ coverage (89% achieved)
- [x] Performance baselines established (specs/performance-baseline.py — 0.316ms avg)
- [x] All 7 MCP tools tested (tests/test_mcp.py — 34 tests)
- [x] Edge case coverage documented
- [x] Discovery log with findings

## Next Steps

1. ✅ Run agent tests and establish performance baselines
2. ✅ Test MCP server tools (34 tests, all passing)
3. ✅ Validate all 50 sample tickets from context (performance-baseline.py)
4. ✅ Document issues discovered (discovery-log.md)
5. Prepare for Part 2 transition (Specialization Phase)
