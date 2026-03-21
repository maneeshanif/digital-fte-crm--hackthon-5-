---
name: fte-mcp-server
description: Create FastMCP server with 7 tools for FTE capabilities. Use when building MCP server or exposing agent tools to Claude/other MCP clients.
---

# FTE MCP Server

Create a FastMCP server that exposes the FTE's capabilities as MCP tools for Claude Code and other MCP clients.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing agent implementation, MCP setup files |
| **Conversation** | MCP server configuration preferences, tool naming, API endpoints |
| **Skill References** | FastMCP framework patterns, tool definitions |
| **User Guidelines** | Server hosting preferences, authentication requirements |

## MCP Server Overview

The server exposes 7 core tools:

1. **search_knowledge_base** - Search product documentation
2. **create_ticket** - Create support ticket with channel tracking
3. **get_customer_history** - Get cross-channel interaction history
4. **send_response** - Send response via appropriate channel
5. **escalate_to_human** - Escalate tickets to human support
6. **analyze_sentiment** - Analyze message sentiment
7. **get_channel_formatting** - Get channel-specific formatting guidelines

## Create MCP Server

### File Structure

```
src/mcp/
├── server.py              # Main FastMCP server
├── tools/
│   ├── knowledge.py       # Knowledge base tools
│   ├── ticket.py         # Ticket management tools
│   ├── sentiment.py      # Sentiment analysis
│   └── channel.py        # Channel formatting
```

### Main Server Implementation

Create `src/mcp/server.py`:

```python
"""
FastMCP Server for Customer Success Agent
Exposes agent capabilities as MCP tools
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional
from enum import Enum
import json

# Import the agent
import sys
sys.path.append('..')
from agent.customer_agent import CustomerAgent, Channel

# Initialize agent
agent = CustomerAgent()

# Create FastMCP server
mcp = FastMCP("customer-success-fte")

@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """
    Search product documentation for relevant information.

    Use this when customer asks questions about product features,
    how to use something, or needs technical information.

    Args:
        query: The customer's question or search terms

    Returns:
        Relevant documentation sections formatted for the agent
    """
    docs = agent.search_knowledge_base(query)
    if not docs:
        return "No relevant documentation found."

    return "\n\n---\n\n".join(docs)

@mcp.tool()
def create_ticket(
    customer_id: str,
    issue: str,
    priority: str,
    channel: str
) -> str:
    """
    Create a support ticket in the system with channel tracking.

    This should be called for every customer interaction to maintain a record.

    Args:
        customer_id: Unique customer identifier (email or phone)
        issue: Description of the customer's issue
        priority: Priority level (low, medium, high, critical)
        channel: Channel where ticket originated (email, whatsapp, web_form)

    Returns:
        Ticket ID and confirmation
    """
    # For prototype: Store in memory
    # For production: Store in PostgreSQL
    ticket_id = f"TKT-{abs(hash(customer_id + issue)) % 10000}"

    return json.dumps({
        "ticket_id": ticket_id,
        "status": "created",
        "customer_id": customer_id,
        "priority": priority,
        "channel": channel,
        "message": f"Ticket created successfully via {channel}"
    })

@mcp.tool()
def get_customer_history(customer_id: str) -> str:
    """
    Get customer's interaction history across ALL channels.

    Use this to provide context-aware responses when a customer
    has interacted before, even on different channels.

    Args:
        customer_id: Unique customer identifier

    Returns:
        Formatted conversation history
    """
    history = agent.get_customer_history(customer_id)

    if not history:
        return f"No previous interactions found for customer {customer_id}"

    formatted_history = []
    for i, interaction in enumerate(history, 1):
        formatted_history.append(
            f"Interaction {i}:\n"
            f"  Channel: {interaction['channel']}\n"
            f"  Sentiment: {interaction['sentiment']}\n"
            f"  Message: {interaction['message']}\n"
            f"  Response: {interaction['response'][:100]}..."
        )

    return "\n\n---\n\n".join(formatted_history)

@mcp.tool()
def send_response(ticket_id: str, message: str, channel: str) -> str:
    """
    Send response to customer via the appropriate channel.

    This is the final step - after analyzing, searching docs, and
    deciding on a response, call this to actually send it.

    Args:
        ticket_id: The ticket ID being responded to
        message: The response message to send
        channel: Channel to send response to (email, whatsapp, web_form)

    Returns:
        Delivery status confirmation
    """
    # For prototype: Simulate sending
    # For production: Integrate with Gmail API, Twilio, etc.

    return json.dumps({
        "ticket_id": ticket_id,
        "status": "sent",
        "channel": channel,
        "delivery_method": {
            "email": "Gmail API",
            "whatsapp": "Twilio WhatsApp",
            "web_form": "Email + API response"
        }.get(channel, "unknown"),
        "message": "Response sent successfully"
    })

@mcp.tool()
def escalate_to_human(ticket_id: str, reason: str, context: str) -> str:
    """
    Escalate a ticket to human support when needed.

    Use this for:
    - Billing issues (refunds, pricing negotiations)
    - Compliance/legal questions
    - Very negative customer sentiment
    - Feature requests (send to product team)

    Args:
        ticket_id: The ticket to escalate
        reason: Why escalation is needed
        context: Full conversation context for the human agent

    Returns:
        Escalation confirmation and ticket ID
    """
    escalation_id = f"ESC-{abs(hash(ticket_id)) % 10000}"

    return json.dumps({
        "escalation_id": escalation_id,
        "original_ticket_id": ticket_id,
        "status": "escalated",
        "reason": reason,
        "assigned_to": "Human Support Team",
        "message": f"Ticket escalated with reason: {reason}"
    })

@mcp.tool()
def analyze_sentiment(message: str) -> str:
    """
    Analyze sentiment of a customer message.

    Use this to detect negative sentiment early and handle
    frustrated customers appropriately.

    Args:
        message: The customer's message

    Returns:
        Sentiment score and recommendation
    """
    sentiment = agent.analyze_sentiment(message)

    recommendations = {
        "positive": "Customer is happy. Maintain helpful tone.",
        "neutral": "Standard support response appropriate.",
        "negative": "Customer is frustrated. Show empathy and consider escalation."
    }

    return json.dumps({
        "sentiment": sentiment,
        "recommendation": recommendations[sentiment]
    })

@mcp.tool()
def get_channel_formatting(channel: str) -> str:
    """
    Get response formatting guidelines for a specific channel.

    Different channels have different expectations for
    length, style, and tone.

    Args:
        channel: The channel (email, whatsapp, web_form)

    Returns:
        Formatting guidelines for channel
    """
    guidelines = {
        "email": {
            "greeting": "Dear [Name]",
            "closing": "Best regards,\nTechFlow Support Team",
            "max_length": 500,
            "style": "Formal, detailed",
            "include_signature": True
        },
        "whatsapp": {
            "greeting": "Hi [Name]!",
            "closing": "Let me know if you need more help!",
            "max_length": 160,
            "style": "Conversational, concise",
            "emojis_allowed": True
        },
        "web_form": {
            "greeting": "Hello [Name],",
            "closing": "We'll get back to you shortly!",
            "max_length": 300,
            "style": "Semi-formal, helpful",
            "emojis_allowed": False
        }
    }

    return json.dumps(guidelines.get(channel, {}))

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
```

## MCP Server Configuration

### Environment Variables

Create `.env` or update existing:

```bash
# MCP Server Configuration
MCP_SERVER_NAME=customer-success-fte
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# MCP Server Options
MCP_SERVER_LOG_LEVEL=INFO
MCP_SERVER_MAX_CONNECTIONS=10
```

### Start Server

```bash
# Run MCP server
uv run python src/mcp/server.py

# Server will listen on stdio for MCP protocol
```

### Test MCP Server

Create `tests/test_mcp_server.py`:

```python
import json
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def test_mcp_tools():
    async with stdio_client() as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [tool.name for tool in tools])

            # Test knowledge search
            result = await session.call_tool("search_knowledge_base", {"query": "Slack integration"})
            print("Search result:", result)

            # Test sentiment analysis
            result = await session.call_tool("analyze_sentiment", {"message": "I'm very frustrated!"})
            print("Sentiment:", result)

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
```

## Tool Usage Patterns

### Typical Workflow

```python
# 1. Analyze incoming message
sentiment = await session.call_tool("analyze_sentiment", {"message": customer_message})

# 2. Check customer history
history = await session.call_tool("get_customer_history", {"customer_id": customer_id})

# 3. Search knowledge base
docs = await session.call_tool("search_knowledge_base", {"query": customer_question})

# 4. Create ticket
ticket = await session.call_tool("create_ticket", {
    "customer_id": customer_id,
    "issue": customer_message,
    "priority": priority,
    "channel": channel
})

# 5. Generate and send response
response = generate_response(docs, channel)
result = await session.call_tool("send_response", {
    "ticket_id": ticket["ticket_id"],
    "message": response,
    "channel": channel
})

# 6. Escalate if needed
if should_escalate:
    await session.call_tool("escalate_to_human", {
        "ticket_id": ticket["ticket_id"],
        "reason": reason,
        "context": full_conversation
    })
```

## Error Handling

### Tool Errors

```python
@mcp.tool()
def search_knowledge_base(query: str) -> str:
    try:
        if not query or not query.strip():
            return json.dumps({"error": "Empty query provided"})

        docs = agent.search_knowledge_base(query)

        if not docs:
            return json.dumps({
                "error": "No results found",
                "query": query,
                "suggestion": "Try rephrasing your question"
            })

        return "\n\n---\n\n".join(docs)

    except Exception as e:
        return json.dumps({
            "error": "Search failed",
            "message": str(e),
            "query": query
        })
```

### Server Errors

```python
if __name__ == "__main__":
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down MCP server...")
    except Exception as e:
        print(f"MCP server error: {e}")
        sys.exit(1)
```

## Available Scripts

### scaffold_mcp_server.py
Automated script that creates:
- Complete `src/mcp/` directory structure
- Main `server.py` with FastMCP setup
- All 7 MCP tools with full implementations
- Submodule files for modularity
- `tests/test_mcp_server.py` with test cases
- All necessary `__init__.py` files

**Usage:**
```bash
python scripts/scaffold_mcp_server.py
```

**What It Creates:**
- FastMCP server instance
- 7 tools: search_knowledge_base, create_ticket, get_customer_history, send_response, escalate_to_human, analyze_sentiment, get_channel_formatting
- Tool descriptions and parameter validation
- JSON return formats for all tools
- Integration with CustomerAgent

### assets/ directory structure
```
fte-mcp-server/
├── SKILL.md                          # Main skill documentation
├── scripts/
│   └── scaffold_mcp_server.py          # Automated MCP server scaffolding
├── assets/
│   └── server-config.json              # Server configuration template
└── references/
    └── mcp-tools-reference.md         # Complete tool specifications
```

## Next Steps

After MCP server:
1. Test all 7 tools with sample data
2. Validate tool responses match expected outputs
3. Run testing and validation using `fte-testing-validator` skill
