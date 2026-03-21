# MCP Server Tools Reference

Complete reference for all 7 MCP tools exposed by the FTE server.

## Tool List

1. **search_knowledge_base** - Search product documentation
2. **create_ticket** - Create support ticket
3. **get_customer_history** - Get cross-channel history
4. **send_response** - Send response via channel
5. **escalate_to_human** - Escalate to human support
6. **analyze_sentiment** - Analyze message sentiment
7. **get_channel_formatting** - Get channel guidelines

## Tool Specifications

### search_knowledge_base

**Purpose:** Search product documentation for relevant information

**When to Use:**
- Customer asks product questions
- Customer needs technical information
- Customer mentions specific features

**Parameters:**
```python
query: str  # The customer's question or search terms
```

**Returns:**
```python
str  # Relevant documentation sections
```

**Example:**
```python
result = search_knowledge_base("How do I integrate Slack?")
# Returns: Slack integration documentation
```

---

### create_ticket

**Purpose:** Create support ticket with channel tracking

**When to Use:**
- Every customer interaction
- To maintain ticket record
- Track channel origins

**Parameters:**
```python
customer_id: str   # Unique customer identifier
issue: str        # Description of customer's issue
priority: str      # low|medium|high|critical
channel: str       # email|whatsapp|web_form
```

**Returns:**
```python
{
    "ticket_id": "TKT-1234",
    "status": "created",
    "customer_id": "customer@example.com",
    "priority": "high",
    "channel": "email",
    "message": "Ticket created successfully via email"
}
```

**Example:**
```python
result = create_ticket(
    customer_id="john@example.com",
    issue="Cannot login to account",
    priority="high",
    channel="email"
)
```

---

### get_customer_history

**Purpose:** Get customer's interaction history across ALL channels

**When to Use:**
- Customer has interacted before
- Need context for response
- Identify cross-channel behavior

**Parameters:**
```python
customer_id: str  # Unique customer identifier
```

**Returns:**
```python
str  # Formatted conversation history
```

**Example:**
```python
history = get_customer_history("john@example.com")
# Returns: All interactions across email, WhatsApp, web_form
```

---

### send_response

**Purpose:** Send response to customer via appropriate channel

**When to Use:**
- After generating response
- After escalation decision
- Final step in processing

**Parameters:**
```python
ticket_id: str  # Ticket being responded to
message: str    # Response message to send
channel: str     # email|whatsapp|web_form
```

**Returns:**
```python
{
    "ticket_id": "TKT-1234",
    "status": "sent",
    "channel": "email",
    "delivery_method": "Gmail API",
    "message": "Response sent successfully"
}
```

**Delivery Methods:**
- Email → Gmail API
- WhatsApp → Twilio WhatsApp
- Web Form → Email + API response

---

### escalate_to_human

**Purpose:** Escalate ticket to human support

**When to Use:**
- Billing issues (refunds, pricing negotiations)
- Compliance/legal questions
- Very negative customer sentiment
- Feature requests

**Parameters:**
```python
ticket_id: str  # Ticket to escalate
reason: str     # Why escalation is needed
context: str    # Full conversation context
```

**Returns:**
```python
{
    "escalation_id": "ESC-5678",
    "original_ticket_id": "TKT-1234",
    "status": "escalated",
    "reason": "Negative customer sentiment detected",
    "assigned_to": "Human Support Team",
    "message": "Ticket escalated with reason: Negative customer sentiment detected"
}
```

---

### analyze_sentiment

**Purpose:** Analyze sentiment of customer message

**When to Use:**
- Every incoming message
- Detect negative sentiment early
- Handle frustrated customers

**Parameters:**
```python
message: str  # Customer's message
```

**Returns:**
```python
{
    "sentiment": "negative",
    "recommendation": "Customer is frustrated. Show empathy and consider escalation."
}
```

**Recommendations:**
- **positive:** Customer is happy. Maintain helpful tone.
- **neutral:** Standard support response appropriate.
- **negative:** Customer is frustrated. Show empathy and consider escalation.

---

### get_channel_formatting

**Purpose:** Get response formatting guidelines for specific channel

**When to Use:**
- Before sending any response
- Ensure channel-appropriate formatting
- Style responses correctly

**Parameters:**
```python
channel: str  # email|whatsapp|web_form
```

**Returns:**
```python
{
    "greeting": "Dear [Name]",
    "closing": "Best regards,\\nTechFlow Support Team",
    "max_length": 500,
    "style": "Formal, detailed",
    "include_signature": True,
    "emojis_allowed": False
}
```

**Channel Guidelines:**

| Channel | Greeting | Closing | Max Length | Style | Emojis |
|---------|----------|---------|------------|-------|---------|
| email | "Dear [Name]" | "Best regards,\\nTeam" | 500 words | Formal, detailed | No |
| whatsapp | "Hi [Name]!" | "Let me know if you need more help!" | 160 chars | Conversational | Yes |
| web_form | "Hello [Name]," | "We'll get back to you shortly!" | 300 words | Semi-formal | No |

## Typical Workflow

```python
# 1. Analyze incoming message
sentiment = analyze_sentiment(customer_message)

# 2. Check customer history
history = get_customer_history(customer_id)

# 3. Search knowledge base
docs = search_knowledge_base(customer_question)

# 4. Create ticket
ticket = create_ticket(
    customer_id=customer_id,
    issue=customer_message,
    priority=priority,
    channel=channel
)

# 5. Generate and send response
response = generate_response(docs, channel)
result = send_response(
    ticket_id=ticket["ticket_id"],
    message=response,
    channel=channel
)

# 6. Escalate if needed
if should_escalate:
    escalate_to_human(
        ticket_id=ticket["ticket_id"],
        reason=reason,
        context=full_conversation
    )
```

## MCP Server Configuration

### Environment Variables
```bash
MCP_SERVER_NAME=customer-success-fte
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
MCP_SERVER_LOG_LEVEL=INFO
```

### Start Server
```bash
uv run python src/mcp/server.py
```

### Server Modes
- **stdio:** Standard input/output (default)
- **sse:** Server-Sent Events (for web clients)
- **ws:** WebSocket (for real-time connections)

## Testing MCP Tools

### Using MCP Client CLI
```bash
uv run python -m mcp.client.cli stdio
```

### Using Python Client
```python
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def test_tools():
    async with stdio_client() as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()

            # Call tool
            result = await session.call_tool(
                "search_knowledge_base",
                {"query": "Slack integration"}
            )

            print(result)
```
