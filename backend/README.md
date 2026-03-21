# Customer Success Digital FTE — Backend (Phase 1 Incubation)

## What This Is

A working prototype of an AI Customer Success agent that handles support inquiries across
three channels (Email, WhatsApp, Web Form). Built in Phase 1 of the Digital FTE Factory Hackathon.

---

## How to Run

```bash
# Install dependencies
uv sync --dev

# Run all tests
uv run python -m pytest tests/ -v

# Run with coverage report
uv run python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Run performance baseline on all 50 sample tickets
uv run python specs/performance-baseline.py

# Start the MCP server
PYTHONPATH=src uv run python -m mcp_server.server
```

---

## Folder Overview

```
backend/
├── context/       ← input data the agent reads (knowledge base)
├── src/           ← all code (agent + MCP server)
├── tests/         ← test files
└── specs/         ← documentation of decisions and discoveries
```

---

## context/ — The Knowledge Base

This folder is the **brain food** for the agent. These are plain text/JSON files that the
agent reads at runtime to answer questions and make decisions. No code here — only data.

```
context/
├── product-docs.md         ← HOW the product works (features, use cases, troubleshooting)
├── escalation-rules.md     ← WHEN to hand off to a human
├── company-profile.md      ← WHO the company is (background, brand tone)
├── brand-voice.md          ← HOW to write responses (tone, style, channel rules)
└── sample-tickets.json     ← 50 EXAMPLE tickets used to test the system
```

### What each file contains and who reads it

**`product-docs.md`**
- Contains: TechFlow's features (Workflow Builder, Integrations, Analytics, Security),
  troubleshooting steps, pricing tiers (Starter $49 / Pro $199 / Enterprise custom)
- Read by: `search_knowledge_base()` in `customer_agent.py` — loaded once on startup,
  then split into sections and scored by keyword overlap for each incoming message
- Used to: build the body of every response

**`escalation-rules.md`**
- Contains: 5 "always escalate" triggers (billing, compliance, outage, negative sentiment,
  feature requests) and 3 categories the agent can handle on its own
- Read by: `check_escalation()` in `customer_agent.py` — loaded fresh on every call
- Used to: decide whether to reply directly or flag for a human agent

**`company-profile.md`**
- Contains: TechFlow company overview, product description, target customers, brand voice summary
- Read by: nobody in code right now — it is **reference context** for the agent/developer
  to understand the business. Will be fed into LLM prompts in Phase 2.
- Used to: inform how responses should feel (professional, customer-success focused)

**`brand-voice.md`**
- Contains: tone rules (professional, helpful, empathetic, concise), channel-specific
  greeting/closing templates, length limits per channel, phrases to use vs avoid
- Read by: nobody in code right now — its rules are **manually baked into**
  `generate_response()` and `_get_greeting()` / `_get_closing()` in `customer_agent.py`
- Used to: the generate_response() logic directly implements these rules in code

**`sample-tickets.json`**
- Contains: 50 real-looking support tickets across all 3 channels with fields:
  `id, channel, customer, subject, message, category, priority, sentiment`
- Read by: `specs/performance-baseline.py` — loops through all 50 tickets,
  runs each through the agent, measures accuracy and speed
- Used to: validate the system works and measure baseline performance

---

## src/ — The Code

### src/agent/customer_agent.py — The Core Brain

This is where all the actual thinking happens. Everything else just calls into this file.

**What it does, step by step, when a message arrives:**

```
Step 1  analyze_sentiment(message)
        ↓ scans message for keyword lists (12 negative / 8 positive words)
        ↓ counts matches, compares
        → returns: POSITIVE / NEUTRAL / NEGATIVE

Step 2  determine_priority(message, sentiment)
        ↓ checks for urgent keywords ("urgent", "asap", "outage", "system down"…)
        ↓ if urgent → CRITICAL
        ↓ if negative sentiment → HIGH
        ↓ if has "?" → MEDIUM
        ↓ otherwise → LOW
        → returns: CRITICAL / HIGH / MEDIUM / LOW

Step 3  search_knowledge_base(message)
        ↓ opens context/product-docs.md (loaded at startup)
        ↓ splits file into sections on "## " headers
        ↓ for each section: count how many message words appear in it
        ↓ sorts sections by score, takes top 3
        → returns: list of 3 most relevant doc sections

Step 4  generate_response(message, docs, channel, name, sentiment)
        ↓ picks greeting template based on channel + customer name
        ↓ stitches first 200 chars from each of the 3 doc sections into body
        ↓ if sentiment=NEGATIVE → adds empathy note
        ↓ picks closing based on channel
        ↓ email: full greeting + body + closing (up to 500 words)
        ↓ whatsapp: short inline format (body truncated to 160 chars)
        ↓ web_form: greeting + body + closing (up to 300 words)
        → returns: formatted response string

Step 5  check_escalation(message, sentiment, priority, category)
        ↓ opens context/escalation-rules.md
        ↓ checks these 5 triggers in order:
        ↓   1. sentiment == NEGATIVE → escalate
        ↓   2. billing keywords in message → escalate
        ↓   3. compliance keywords in message → escalate
        ↓   4. priority == CRITICAL → escalate
        ↓   5. category == feature_request → escalate
        ↓ none match → no escalation
        → returns: (True/False, reason string)

Step 6  detect_category(message)
        ↓ checks message against 5 keyword groups
        ↓ technical / billing / feature_request / compliance / pricing
        ↓ first match wins; no match → "general"
        → returns: category string

Step 7  store_conversation(customer_id, message, response, channel, sentiment)
        ↓ appends to in-memory dict keyed by customer_id
        ↓ stores: message, response, channel, sentiment, timestamp
        → nothing returned, data lives in RAM only
```

**Final return dict from process_message():**
```python
{
  "response":          "Dear John, Based on your question...",
  "sentiment":         Sentiment.NEGATIVE,
  "should_escalate":   True,
  "escalation_reason": "Negative customer sentiment detected",
  "priority":          Priority.HIGH,
  "category":          "technical",
  "channel":           "email"
}
```

---

### src/mcp_server/server.py — The MCP Interface

Wraps the agent as 7 callable tools so external systems (like Claude or other MCP clients)
can use them over the MCP protocol.

**Each tool and what it does internally:**

| Tool | Calls | Returns |
|---|---|---|
| `search_knowledge_base(query)` | `agent.search_knowledge_base()` | doc sections joined by `---` |
| `create_ticket(customer_id, issue, priority, channel)` | nothing — generates `hash()` ID | JSON with ticket_id, status |
| `get_customer_history(customer_id)` | `agent.get_customer_history()` | formatted interaction list |
| `send_response(ticket_id, message, channel)` | nothing — simulated | JSON with delivery_method |
| `escalate_to_human(ticket_id, reason, context)` | nothing — generates `hash()` ID | JSON with escalation_id |
| `analyze_sentiment(message)` | `agent.analyze_sentiment()` | JSON with sentiment + recommendation |
| `get_channel_formatting(channel)` | nothing — hardcoded dict | JSON with greeting, closing, max_length, style |

The MCP server does **not** replace the agent — it just exposes the agent's capabilities
as tools that can be invoked remotely.

---

### src/channels/ — Placeholder

Empty for now. In Phase 2 this will hold the actual channel adapters:
- `gmail.py` → reads email via Gmail API
- `twilio.py` → reads/sends WhatsApp via Twilio
- `web_form.py` → receives form submissions via FastAPI endpoint

---

## specs/ — Decisions and Discoveries

This folder is the **written output of Phase 1 incubation**. Not code — documentation.
Required by the hackathon as proof that the incubation process happened.

```
specs/
├── customer-success-fte-spec.md   ← master blueprint of the system
├── skills.md                      ← the 7 things this agent can do
├── discovery-log.md               ← what was learned during exploration
└── performance-baseline.py        ← script that measures system performance
```

**`customer-success-fte-spec.md`**
- The **master spec** — defines supported channels, escalation rules, tool list,
  known limitations, and the full upgrade plan for Phase 2
- Think of it as the contract: "here is exactly what this system does and doesn't do"

**`skills.md`**
- The **agent skills manifest** — lists all 7 skills with: when to use, inputs, outputs,
  which MCP tool implements it, and an example
- Required deliverable from Exercise 1.5 of the hackathon

**`discovery-log.md`**
- **What was discovered during incubation** — channel-specific patterns, edge cases found,
  technical decisions made, and open questions for Phase 2
- Required deliverable from Exercise 1.1 of the hackathon

**`performance-baseline.py`**
- Loads all 50 tickets from `context/sample-tickets.json`
- Runs each through the agent, measures response time and sentiment accuracy
- Prints a full report (per-channel breakdown, mismatches, category distribution)
- Lives in specs/ because it is a measurement tool, not production code

---

## Full Data Journey — One Message Through the System

```
context/product-docs.md ──────────────────────┐
context/escalation-rules.md ──────────────────┤
                                               ▼
Customer message ──► CustomerAgent.process_message()
(any channel)              │
                           ├─ analyze_sentiment()     → no files read
                           ├─ determine_priority()    → no files read
                           ├─ search_knowledge_base() → reads product-docs.md
                           ├─ generate_response()     → uses brand-voice rules (hardcoded)
                           ├─ check_escalation()      → reads escalation-rules.md
                           ├─ detect_category()       → no files read
                           └─ store_conversation()    → writes to in-memory dict (RAM)
                                               │
                                               ▼
                                    result dict returned
                                               │
                           ┌───────────────────┴──────────────────────┐
                           ▼                                           ▼
               MCP tools (mcp_server/server.py)            tests/ validate it
               wrap result for external callers             specs/performance-baseline.py
                                                            measures it
```

---

## Phase 1 Results

| Metric | Value |
|---|---|
| Tests passing | 47 / 47 |
| Code coverage | 89% |
| Avg response time | 0.316 ms |
| Sentiment accuracy | 72% (keyword-based, expected) |
| Escalation rate | 48% across 50 tickets |
| MCP tools | 7 |
| Sample tickets | 50 |
| Channels | Email, WhatsApp, Web Form |

---

## Known Limitations (Phase 1 by Design)

| Limitation | Reason | Phase 2 Fix |
|---|---|---|
| No database | Prototype uses RAM | PostgreSQL via Neon DB |
| 72% sentiment accuracy | Keyword-only matching | LLM-based sentiment |
| Template responses | No LLM calls | Claude/OpenAI response generation |
| Simulated channel delivery | No real API keys | Gmail API + Twilio |
| No auth | Prototype only | API key / JWT in Phase 2 |
| History lost on restart | In-memory storage | Persistent DB |
