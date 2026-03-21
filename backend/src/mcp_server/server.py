"""
FastMCP Server for Customer Success Agent
Exposes agent capabilities as MCP tools
"""

from fastmcp import FastMCP
from typing import Optional
from enum import Enum
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

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
    # Run MCP server
    print("Starting MCP server...")
    print("Press Ctrl+C to stop")
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nMCP server stopped")
