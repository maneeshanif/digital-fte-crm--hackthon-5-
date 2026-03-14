# Part 1: The Incubation Phase (Hours 1-16)

## Overview

In this phase, you'll build a **working prototype** of a Customer Success Digital FTE using Claude Code as your Agent Factory. The prototype will discover requirements, validate approaches, and establish patterns that will be refined into production code in Part 2.

## Your Tech Stack for Part 1

### Backend
- **Language:** Python
- **Package Manager:** `uv` (fast Python package manager)
- **MCP Server:** `fastmcp` (for building MCP servers)
- **Agent:** Claude Code (General Agent) for exploration

### Frontend
- **Framework:** Next.js
- **UI:** React components
- **Purpose:** Web Support Form (prototype version)

### Database
- **Platform:** Neon DB (Serverless PostgreSQL)
- **Usage:** For storing prototype data (customers, tickets, conversations)

---

## Phase 1.1: Initial Exploration (2-3 hours)

### Setup Your Development Environment

```bash
# Initialize Python project with uv
uv init customer-success-fte
cd customer-success-fte

# Create project structure
mkdir -p context src/agent src/channels src/mcp tests specs web-form

# Install dependencies
uv add fastmcp openai anthropic psycopg2-binary python-dotenv
```

### Create Your Development Dossier

#### `context/company-profile.md`
```markdown
# Company Profile - TechFlow SaaS

## Company Overview
TechFlow is a growing SaaS platform offering workflow automation for enterprises.

## Product Description
TechFlow helps businesses automate their internal processes with:
- Visual workflow builder
- Integration with 50+ third-party tools
- Real-time analytics and reporting
- Enterprise-grade security (SOC2 compliant)

## Target Customers
- Mid-size to large enterprises (500-5000 employees)
- Industries: Tech, Finance, Healthcare, Manufacturing
- Decision makers: CTOs, Operations Managers, IT Directors

## Brand Voice
- Professional yet approachable
- Concise and direct
- Data-driven in communication
- Customer success focused
```

#### `context/product-docs.md`
```markdown
# TechFlow Product Documentation

## Core Features

### 1. Workflow Builder
The visual drag-and-drop workflow builder allows users to create automated processes without coding.
- Drag nodes from the sidebar
- Connect nodes to define logic flow
- Set conditions and triggers
- Test workflows in sandbox mode

### 2. Integrations
Connect TechFlow with your existing tools:
- Salesforce, HubSpot (CRM)
- Slack, Microsoft Teams (Communication)
- Google Drive, Dropbox (Storage)
- Custom API webhooks
- Enterprise ERPs (SAP, Oracle)

### 3. Analytics Dashboard
Real-time metrics include:
- Workflow execution time
- Success/failure rates
- Bottleneck identification
- Resource utilization

### 4. Security Features
- SOC2 Type II certified
- Role-based access control (RBAC)
- Audit logs (90-day retention)
- Data encryption at rest and in transit
- SSO with Okta, Azure AD, Google Workspace

## Common Use Cases

### Automated Document Processing
Upload documents → Extract data → Route to appropriate department

### Customer Onboarding
New signup → Send welcome email → Schedule demo → Track engagement

### Approval Workflows
Request submitted → Manager review → Auto-approve if criteria met → Notify

## Troubleshooting Guide

### Issue: Workflow not executing
**Solutions:**
1. Check if triggers are properly configured
2. Verify all connected nodes have valid credentials
3. Review error logs in the Analytics tab
4. Ensure workflow is published (not just saved)

### Issue: Integration failure
**Solutions:**
1. Verify API credentials are current
2. Check if third-party service is operational
3. Review rate limits (1000 requests/hour for free tier)
4. Test connection in Integration Settings

### Issue: Slow workflow execution
**Solutions:**
1. Optimize complex conditional logic
2. Reduce number of parallel branches
3. Use batch processing for bulk operations
4. Upgrade to Enterprise plan for more resources

## Pricing
- Starter: $49/month (5 workflows, 1000 executions)
- Professional: $199/month (unlimited workflows, 10,000 executions)
- Enterprise: Custom pricing (unlimited, priority support, dedicated account manager)
```

#### `context/sample-tickets.json`
```json
{
  "tickets": [
    {
      "id": 1,
      "channel": "email",
      "customer": {
        "email": "john.doe@acme.com",
        "name": "John Doe",
        "company": "Acme Corp"
      },
      "subject": "Workflow not executing - urgent!",
      "message": "Hello, I've been trying to set up a document processing workflow for the past 3 hours. It won't execute no matter what I do. The workflow is published and all nodes are connected. I'm losing patience with this platform.",
      "category": "technical",
      "priority": "high",
      "sentiment": "negative"
    },
    {
      "id": 2,
      "channel": "whatsapp",
      "customer": {
        "phone": "+15551234567",
        "name": "Sarah Chen"
      },
      "message": "Hi! How do I connect my Slack workspace?",
      "category": "integration",
      "priority": "low",
      "sentiment": "positive"
    },
    {
      "id": 3,
      "channel": "web_form",
      "customer": {
        "email": "mike@startup.io",
        "name": "Mike Johnson"
      },
      "subject": "Feature Request",
      "message": "Can you add support for Asana integration? We use Asana extensively and it would be great to have it in TechFlow.",
      "category": "feature_request",
      "priority": "medium",
      "sentiment": "neutral"
    },
    {
      "id": 4,
      "channel": "email",
      "customer": {
        "email": "executive@megacorp.com",
        "name": "David Smith",
        "company": "MegaCorp"
      },
      "subject": "RE: Enterprise License - Refund Request",
      "message": "We've decided not to move forward with TechFlow. The platform doesn't meet our compliance requirements. Please process our refund of $50,000 for the upfront payment.",
      "category": "billing",
      "priority": "critical",
      "sentiment": "negative"
    },
    {
      "id": 5,
      "channel": "whatsapp",
      "customer": {
        "phone": "+15559876543",
        "name": "Emma Wilson"
      },
      "message": "My workflow is super slow. Takes like 5 mins to run. Help?",
      "category": "technical",
      "priority": "high",
      "sentiment": "neutral"
    },
    {
      "id": 6,
      "channel": "web_form",
      "customer": {
        "email": "developer@tech.co",
        "name": "Alex Kim"
      },
      "subject": "API Question",
      "message": "What's the rate limit for webhook integrations? I need to process about 2000 requests per hour for my use case.",
      "category": "technical",
      "priority": "medium",
      "sentiment": "neutral"
    },
    {
      "id": 7,
      "channel": "email",
      "customer": {
        "email": "it-manager@hospital.org",
        "name": "Dr. Robert Chen",
        "company": "City Hospital"
      },
      "subject": "Security Question - HIPAA Compliance",
      "message": "We're a healthcare organization and need to ensure TechFlow is HIPAA compliant. Can you provide your BAA and security documentation?",
      "category": "compliance",
      "priority": "high",
      "sentiment": "neutral"
    },
    {
      "id": 8,
      "channel": "whatsapp",
      "customer": {
        "phone": "+15555555555",
        "name": "Lisa Park"
      },
      "message": "How much for 50 users? Need pricing info ASAP",
      "category": "pricing",
      "priority": "medium",
      "sentiment": "neutral"
    },
    {
      "id": 9,
      "channel": "web_form",
      "customer": {
        "email": "new.user@company.com",
        "name": "Jamie Brown"
      },
      "subject": "Can't login",
      "message": "I just signed up but can't login. Says invalid credentials. I'm using the correct email and password.",
      "category": "technical",
      "priority": "high",
      "sentiment": "negative"
    },
    {
      "id": 10,
      "channel": "email",
      "customer": {
        "email": "happy.user@success.com",
        "name": "Jennifer Taylor"
      },
      "subject": "Love the product! One question",
      "message": "TechFlow has been amazing for our team! We've automated 15 workflows already. Quick question - is there a way to export workflow data to CSV for our weekly reports?",
      "category": "technical",
      "priority": "low",
      "sentiment": "positive"
    }
  ]
}
```

#### `context/escalation-rules.md`
```markdown
# Escalation Rules

## Always Escalate to Human Support

1. **Billing Issues**
   - Refund requests
   - Payment disputes
   - Pricing negotiations (Enterprise tier)

2. **Compliance & Legal**
   - HIPAA, GDPR, SOC2 documentation requests
   - Legal questions
   - Contract modifications

3. **High-Priority Technical Issues**
   - Urgent system outages
   - Data loss concerns
   - Security incidents

4. **Negative Sentiment**
   - Customers with sentiment score < 0.3
   - Multiple failed attempts to resolve
   - Threatening language or lawsuits

5. **Feature Requests**
   - All feature requests go to product team
   - Tag by priority based on customer tier

## Agent Can Handle

1. **Product Information**
   - Feature questions
   - How-to guidance
   - Troubleshooting (non-urgent)

2. **General Support**
   - Account setup
   - Basic integration questions
   - Usage best practices

3. **Bug Reporting**
   - Collect bug reports
   - Provide workarounds if known
   - Escalate if no workaround exists
```

#### `context/brand-voice.md`
```markdown
# Brand Voice Guidelines

## Tone
- **Professional:** Use proper grammar, avoid slang
- **Helpful:** Focus on solving the customer's problem
- **Empathetic:** Acknowledge frustrations when present
- **Concise:** Get to the point quickly, especially on chat channels

## Channel-Specific Guidelines

### Email (Gmail)
- Greeting: "Dear [Name]" or "Hi [Name]"
- Closing: "Best regards" or "Sincerely"
- Length: 200-500 words
- Style: Detailed, include step-by-step instructions
- Signature: Include "TechFlow Support Team"

### WhatsApp
- Greeting: "Hi [Name]" or "Hello!"
- Closing: "Let me know if you need more help!"
- Length: 160 characters preferred, max 300
- Style: Conversational, use emojis occasionally (✅, 👍)
- Quick responses preferred

### Web Form
- Greeting: "Hello [Name]"
- Closing: "We'll get back to you shortly!"
- Length: 100-300 words
- Style: Semi-formal, helpful
- Acknowledge receipt immediately

## Phrases to Use
- "I'd be happy to help you with that"
- "Let me check the documentation for you"
- "Here's what you need to do:"
- "Is there anything else I can assist with?"

## Phrases to Avoid
- "I don't know" (Instead: "Let me find that information for you")
- "That's not possible" (Instead: "Let me see what options are available")
- "You need to..." (Instead: "Here's how you can...")
```

---

## Exercise 1.2: Prototype the Core Loop (4-5 hours)

### Task: Build the Basic Interaction

Create a prototype that:
1. Takes a customer message as input (with channel metadata)
2. Normalizes the message regardless of source channel
3. Searches the product docs for relevant information
4. Generates a helpful response
5. Formats response appropriately for the channel
6. Decides if escalation is needed

### Create the Prototype File

#### `src/agent/customer_agent.py`

```python
"""
Customer Success Agent Prototype
A working prototype that handles customer queries across channels.
"""

from typing import Dict, Optional, List
from enum import Enum
import re
import json

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CustomerAgent:
    """Prototype Customer Success Agent"""

    def __init__(self):
        self.load_knowledge_base()
        self.conversation_memory = {}

    def load_knowledge_base(self):
        """Load product documentation from context folder"""
        with open('context/product-docs.md', 'r') as f:
            self.knowledge_base = f.read()

    def process_message(
        self,
        message: str,
        channel: Channel,
        customer_id: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> Dict:
        """
        Process a customer message and generate a response.

        Args:
            message: Customer's message
            channel: Source channel (email, whatsapp, web_form)
            customer_id: Unique customer identifier
            customer_name: Customer's name for personalization

        Returns:
            Dict containing response, sentiment, and escalation decision
        """
        # Step 1: Analyze sentiment
        sentiment = self.analyze_sentiment(message)

        # Step 2: Determine priority
        priority = self.determine_priority(message, sentiment)

        # Step 3: Search knowledge base
        relevant_docs = self.search_knowledge_base(message)

        # Step 4: Generate response
        response = self.generate_response(
            message=message,
            relevant_docs=relevant_docs,
            channel=channel,
            customer_name=customer_name,
            sentiment=sentiment
        )

        # Step 5: Decide escalation
        should_escalate, escalation_reason = self.check_escalation(
            message=message,
            sentiment=sentiment,
            priority=priority,
            category=self.detect_category(message)
        )

        # Step 6: Store in memory
        if customer_id:
            self.store_conversation(
                customer_id=customer_id,
                message=message,
                response=response,
                channel=channel,
                sentiment=sentiment
            )

        return {
            "response": response,
            "sentiment": sentiment,
            "should_escalate": should_escalate,
            "escalation_reason": escalation_reason,
            "priority": priority,
            "category": self.detect_category(message)
        }

    def analyze_sentiment(self, message: str) -> Sentiment:
        """Simple sentiment analysis based on keywords"""
        negative_words = [
            'angry', 'frustrated', 'hate', 'terrible', 'worst',
            'losing patience', 'waste of time', 'useless',
            'refund', 'cancel', 'threaten', 'lawsuit'
        ]

        positive_words = [
            'love', 'amazing', 'great', 'excellent', 'happy',
            'thanks', 'thank you', 'helpful', 'appreciate'
        ]

        message_lower = message.lower()

        negative_count = sum(1 for word in negative_words if word in message_lower)
        positive_count = sum(1 for word in positive_words if word in message_lower)

        if negative_count > positive_count:
            return Sentiment.NEGATIVE
        elif positive_count > negative_count:
            return Sentiment.POSITIVE
        else:
            return Sentiment.NEUTRAL

    def determine_priority(self, message: str, sentiment: Sentiment) -> Priority:
        """Determine ticket priority based on content and sentiment"""
        urgent_keywords = [
            'urgent', 'asap', 'emergency', 'critical', 'immediately',
            'system down', 'outage', 'cannot login', 'losing money'
        ]

        message_lower = message.lower()

        if any(keyword in message_lower for keyword in urgent_keywords):
            return Priority.CRITICAL
        elif sentiment == Sentiment.NEGATIVE:
            return Priority.HIGH
        elif '?' in message:
            return Priority.MEDIUM
        else:
            return Priority.LOW

    def search_knowledge_base(self, query: str) -> List[str]:
        """
        Simple keyword-based search of product documentation.

        For prototype: Use simple string matching
        For production: Use vector similarity search
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        # Split knowledge base into sections
        sections = self.knowledge_base.split('\n## ')

        scored_sections = []
        for section in sections:
            # Score based on keyword overlap
            section_lower = section.lower()
            section_words = set(re.findall(r'\w+', section_lower))
            overlap = len(query_words & section_words)

            if overlap > 0:
                scored_sections.append((section, overlap))

        # Sort by overlap score and return top 3
        scored_sections.sort(key=lambda x: x[1], reverse=True)
        return [section[0] for section in scored_sections[:3]]

    def generate_response(
        self,
        message: str,
        relevant_docs: List[str],
        channel: Channel,
        customer_name: Optional[str],
        sentiment: Sentiment
    ) -> str:
        """Generate a response appropriate for the channel"""

        greeting = self._get_greeting(channel, customer_name)
        body = self._build_response_body(message, relevant_docs)
        closing = self._get_closing(channel)
        escalation_note = self._get_escalation_note(sentiment)

        if channel == Channel.EMAIL:
            return f"{greeting}\n\n{body}\n{escalation_note}\n\n{closing}"
        elif channel == Channel.WHATSAPP:
            return f"{greeting} {body[:160]}... {closing}"
        else:  # web_form
            return f"{greeting}\n\n{body}\n{closing}"

    def _get_greeting(self, channel: Channel, name: Optional[str]) -> str:
        if name:
            name = name.split()[0]  # First name only
        else:
            name = "there"

        if channel == Channel.EMAIL:
            return f"Dear {name},"
        elif channel == Channel.WHATSAPP:
            return f"Hi {name}!"
        else:  # web_form
            return f"Hello {name},"

    def _build_response_body(self, message: str, docs: List[str]) -> str:
        """Build the main response body from relevant docs"""
        if not docs:
            return "I couldn't find specific information about your question. Let me escalate this to a human specialist who can help you better."

        # Extract relevant information from docs
        response_parts = []
        for doc in docs:
            # Take first 200 chars of each relevant section
            relevant_part = doc[:200]
            response_parts.append(relevant_part)

        body = "Based on your question, here's what I found:\n\n"
        body += "\n\n".join(response_parts)
        return body

    def _get_closing(self, channel: Channel) -> str:
        if channel == Channel.EMAIL:
            return "Best regards,\nTechFlow Support Team"
        elif channel == Channel.WHATSAPP:
            return "Let me know if you need more help! 👍"
        else:  # web_form
            return "We'll get back to you shortly!"

    def _get_escalation_note(self, sentiment: Sentiment) -> str:
        if sentiment == Sentiment.NEGATIVE:
            return "I understand this is frustrating for you. A human specialist will review your case shortly."
        return ""

    def check_escalation(
        self,
        message: str,
        sentiment: Sentiment,
        priority: Priority,
        category: str
    ) -> tuple[bool, str]:
        """
        Check if this should be escalated to human support.

        Returns:
            (should_escalate: bool, reason: str)
        """
        # Load escalation rules
        with open('context/escalation-rules.md', 'r') as f:
            escalation_rules = f.read()

        # Check negative sentiment
        if sentiment == Sentiment.NEGATIVE:
            return True, "Negative customer sentiment detected"

        # Check for billing issues
        billing_keywords = ['refund', 'payment', 'pricing', 'discount', 'negotiate']
        if any(kw in message.lower() for kw in billing_keywords):
            return True, "Billing/pricing related inquiry"

        # Check for compliance/legal
        compliance_keywords = ['hipaa', 'gdpr', 'soc2', 'legal', 'compliance', 'baa']
        if any(kw in message.lower() for kw in compliance_keywords):
            return True, "Compliance/legal inquiry"

        # Check critical priority
        if priority == Priority.CRITICAL:
            return True, "Critical priority issue"

        # Check for feature requests
        if category == "feature_request":
            return True, "Feature request - needs product team review"

        return False, ""

    def detect_category(self, message: str) -> str:
        """Detect the category of the customer's inquiry"""
        message_lower = message.lower()

        category_keywords = {
            "technical": ["workflow", "integration", "api", "bug", "error", "login"],
            "billing": ["refund", "payment", "price", "invoice", "billing"],
            "feature_request": ["feature", "add", "support", "can you", "would be great"],
            "compliance": ["security", "hipaa", "gdpr", "soc2", "compliance"],
            "pricing": ["how much", "cost", "pricing", "license", "subscription"]
        }

        for category, keywords in category_keywords.items():
            if any(kw in message_lower for kw in keywords):
                return category

        return "general"

    def store_conversation(
        self,
        customer_id: str,
        message: str,
        response: str,
        channel: Channel,
        sentiment: Sentiment
    ):
        """Store conversation in memory (prototype uses in-memory dict)"""
        if customer_id not in self.conversation_memory:
            self.conversation_memory[customer_id] = []

        self.conversation_memory[customer_id].append({
            "message": message,
            "response": response,
            "channel": channel,
            "sentiment": sentiment,
            "timestamp": str(datetime.now())
        })

    def get_customer_history(self, customer_id: str) -> List[Dict]:
        """Get conversation history for a customer"""
        return self.conversation_memory.get(customer_id, [])

# Example usage
if __name__ == "__main__":
    from datetime import datetime

    agent = CustomerAgent()

    # Test with different channels
    test_messages = [
        {
            "message": "How do I connect my Slack workspace?",
            "channel": Channel.WHATSAPP,
            "customer_name": "Sarah Chen"
        },
        {
            "message": "My workflow isn't executing and I've been trying for hours!",
            "channel": Channel.EMAIL,
            "customer_name": "John Doe"
        },
        {
            "message": "Can you add support for Asana integration?",
            "channel": Channel.WEB_FORM,
            "customer_name": "Mike Johnson"
        }
    ]

    for test in test_messages:
        result = agent.process_message(
            message=test["message"],
            channel=test["channel"],
            customer_name=test["customer_name"]
        )

        print(f"\n{'='*50}")
        print(f"Channel: {test['channel'].value}")
        print(f"Customer: {test['customer_name']}")
        print(f"Message: {test['message']}")
        print(f"\nResponse:\n{result['response']}")
        print(f"\nSentiment: {result['sentiment']}")
        print(f"Priority: {result['priority']}")
        print(f"Escalate: {result['should_escalate']}")
        if result['should_escalate']:
            print(f"Reason: {result['escalation_reason']}")
```

---

## Exercise 1.3: Add Memory and State (3-4 hours)

### Task: Extend the Prototype with Conversation Memory

The agent needs to:
1. Remember context across a conversation
2. Track customer sentiment over time
3. Identify topic switches
4. Handle cross-channel conversations

### Enhance the Agent

Add these methods to `src/agent/customer_agent.py`:

```python
from datetime import datetime
from collections import defaultdict

class CustomerAgent:
    def __init__(self):
        self.load_knowledge_base()
        self.conversation_memory = defaultdict(list)
        self.customer_sentiment_history = defaultdict(list)

    def process_message(self, message: str, channel: Channel, **kwargs) -> Dict:
        # ... existing code ...

        # Track sentiment over time
        self.customer_sentiment_history[customer_id].append({
            "sentiment": sentiment,
            "timestamp": datetime.now()
        })

        # Check for topic switch
        previous_topic = self.detect_topic(
            self.conversation_memory[customer_id][-2]["message"]
            if len(self.conversation_memory[customer_id]) > 1 else None
        ) if customer_id and len(self.conversation_memory[customer_id]) > 1 else None

        current_topic = self.detect_topic(message)

        if previous_topic and previous_topic != current_topic:
            response = self.handle_topic_switch(
                response=response,
                previous_topic=previous_topic,
                current_topic=current_topic
            )

        # ... rest of existing code ...
```

### Add Topic Detection

```python
def detect_topic(self, message: Optional[str]) -> Optional[str]:
    """Detect the topic of a message"""
    if not message:
        return None

    message_lower = message.lower()

    topic_keywords = {
        "workflow": ["workflow", "automation", "process"],
        "integration": ["integration", "connect", "api", "webhook"],
        "billing": ["payment", "refund", "price", "invoice"],
        "troubleshooting": ["error", "problem", "not working", "issue"],
        "features": ["feature", "add", "support", "new"]
    }

    for topic, keywords in topic_keywords.items():
        if any(kw in message_lower for kw in keywords):
            return topic

    return "general"

def handle_topic_switch(self, response: str, previous_topic: str, current_topic: str) -> str:
    """Add acknowledgment when customer switches topics"""
    acknowledgment = f"\n\nI see we're switching topics from {previous_topic} to {current_topic}. Let me help with that."
    return response + acknowledgment
```

---

## Exercise 1.4: Build the MCP Server with FastMCP (3-4 hours)

### Task: Create an MCP Server using FastMCP

This server will expose your agent's capabilities as MCP tools that can be used by Claude Code and other MCP clients.

### Install FastMCP

```bash
uv add fastmcp
```

### Create MCP Server

#### `src/mcp/server.py`

```python
"""
FastMCP Server for Customer Success Agent
Exposes agent capabilities as MCP tools
"""

from mcp.server.fastmcp import FastMCP
from typing import Optional
from enum import Enum
import json

# Import the agent from previous exercise
import sys
sys.path.append('..')
from agent.customer_agent import CustomerAgent, Channel

# Initialize the agent
agent = CustomerAgent()

# Create FastMCP server
mcp = FastMCP("customer-success-fte")

@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """
    Search product documentation for relevant information.

    Use this when the customer asks questions about product features,
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
    Analyze the sentiment of a customer message.

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
        Formatting guidelines for the channel
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

### Test the MCP Server

```bash
# Start the server
uv run python src/mcp/server.py
```

---

## Exercise 1.5: Define Agent Skills (2-3 hours)

### Task: Create Skill Definitions

Create a skills manifest that defines reusable capabilities.

#### `specs/skills.md`

```markdown
# Customer Success FTE - Agent Skills

## Skill 1: Knowledge Retrieval

**When to use:**
- Customer asks product questions
- Customer needs "how-to" guidance
- Customer mentions specific features

**Inputs:**
- `query`: Customer's question or search terms

**Outputs:**
- Relevant documentation snippets with confidence scores
- Maximum 5 results returned

**Implementation:**
```
tool: search_knowledge_base(query: str) -> str
```

**Examples:**
- Input: "How do I connect Slack?"
- Output: Slack integration instructions from docs

---

## Skill 2: Sentiment Analysis

**When to use:**
- Every incoming customer message
- After sending responses (track sentiment changes)

**Inputs:**
- `message`: Customer message text

**Outputs:**
- `sentiment`: positive/neutral/negative
- `confidence`: Score 0-1
- `recommendation`: How to respond

**Implementation:**
```
tool: analyze_sentiment(message: str) -> str
```

**Examples:**
- Input: "I've been trying for hours and it's still not working!"
- Output: {sentiment: "negative", recommendation: "Show empathy and escalate if needed"}

---

## Skill 3: Escalation Decision

**When to use:**
- After generating initial response
- Before closing a ticket

**Inputs:**
- `conversation_context`: Full conversation history
- `sentiment_trend`: How sentiment has changed
- `category`: Type of inquiry

**Outputs:**
- `should_escalate`: boolean
- `reason`: Explanation of why escalation is needed (or None)

**Implementation:**
```
tool: escalate_to_human(ticket_id, reason, context) -> str
```

**Escalation Triggers:**
1. Sentiment < 0.3 (very negative)
2. Billing issues (refund, payment disputes)
3. Compliance/legal questions
4. Feature requests
5. Priority = critical

---

## Skill 4: Channel Adaptation

**When to use:**
- Before sending any response

**Inputs:**
- `response_text`: Draft response message
- `target_channel`: email/whatsapp/web_form

**Outputs:**
- Formatted response appropriate for the channel

**Implementation:**
```
tool: get_channel_formatting(channel: str) -> str
```

**Channel Guidelines:**

| Channel | Greeting | Closing | Max Length | Style |
|---------|----------|---------|------------|-------|
| Email | "Dear [Name]" | "Best regards" | 500 words | Formal, detailed |
| WhatsApp | "Hi [Name]!" | "Let me know if you need more help!" | 160 chars | Conversational |
| Web Form | "Hello [Name]," | "We'll get back to you!" | 300 words | Semi-formal |

---

## Skill 5: Customer Identification

**When to use:**
- On every incoming message

**Inputs:**
- `message_metadata`: Email, phone, or form submission data

**Outputs:**
- `customer_id`: Unified identifier
- `merged_history`: All previous interactions across channels

**Implementation:**
```
tool: get_customer_history(customer_id: str) -> str
```

**Cross-Channel Matching:**
- Email address → Email + Web Form
- Phone number → WhatsApp
- Merge histories when customer uses multiple channels

---

## Skill 6: Ticket Creation

**When to use:**
- For EVERY customer interaction

**Inputs:**
- `customer_id`: Unique identifier
- `issue`: Problem description
- `priority`: low/medium/high/critical
- `channel`: Source channel

**Outputs:**
- `ticket_id`: Unique ticket identifier

**Implementation:**
```
tool: create_ticket(customer_id, issue, priority, channel) -> str
```

---

## Skill 7: Response Delivery

**When to use:**
- After generating response and deciding on escalation

**Inputs:**
- `ticket_id`: Ticket to respond to
- `message`: Response content
- `channel`: Channel to send via

**Outputs:**
- `delivery_status`: sent/delivery_failed

**Implementation:**
```
tool: send_response(ticket_id, message, channel) -> str
```

**Delivery Methods:**
- Email → Gmail API
- WhatsApp → Twilio WhatsApp API
- Web Form → API response + Email confirmation
```

---

## Part 1 Deliverables Checklist

Before moving to Part 2 (Specialization), ensure you have:

### ☐ Core Prototype
- [ ] Working prototype in `src/agent/customer_agent.py`
- [ ] Handles customer queries from any channel
- [ ] Generates appropriate responses based on product docs
- [ ] Formats responses correctly for each channel

### ☐ Documentation & Discovery
- [ ] `specs/discovery-log.md` - Requirements found during exploration
- [ ] `specs/customer-success-fte-spec.md` - Crystallized specification
- [ ] Context files prepared:
  - [ ] `context/company-profile.md`
  - [ ] `context/product-docs.md`
  - [ ] `context/sample-tickets.json`
  - [ ] `context/escalation-rules.md`
  - [ ] `context/brand-voice.md`

### ☐ MCP Server
- [ ] FastMCP server in `src/mcp/server.py`
- [ ] 7+ tools exposed:
  - [ ] search_knowledge_base
  - [ ] create_ticket
  - [ ] get_customer_history
  - [ ] send_response
  - [ ] escalate_to_human
  - [ ] analyze_sentiment
  - [ ] get_channel_formatting
- [ ] Server can be started and queried

### ☐ Agent Skills
- [ ] Skills defined in `specs/skills.md`
- [ ] Each skill has:
  - [ ] When to use
  - [ ] Inputs/Outputs
  - [ ] Implementation reference
  - [ ] Examples

### ☐ Advanced Features
- [ ] Conversation memory implemented
- [ ] Sentiment tracking over time
- [ ] Topic detection and switches
- [ ] Cross-channel customer identification

### ☐ Edge Cases
- [ ] Edge cases documented in `specs/discovery-log.md`
- [ ] Handling strategies defined for:
  - [ ] Empty messages
  - [ ] Very long messages
  - [ ] Multiple questions in one message
  - [ ] Channel switching mid-conversation
  - [ ] Angry customers

### ☐ Testing
- [ ] Tested with sample tickets from all channels
- [ ] Performance baseline recorded:
  - [ ] Average response time: ___ seconds
  - [ ] Accuracy on test set: ___%
  - [ ] Escalation rate: ___%
- [ ] Test cases saved in `tests/prototype_tests.py`

### ☐ Ready for Part 2
- [ ] Prototype tested and validated
- [ ] All requirements documented
- [ ] Tools working as expected
- [ ] Clear understanding of what needs to be productionized

---

## Part 1 Success Criteria

You're ready to move to Part 2 when:

✅ You can input a customer message from any channel and get a relevant, helpful response
✅ The agent correctly identifies when to escalate to humans
✅ You have documentation of all discovered requirements
✅ Your MCP server is working and tools are tested
✅ You've identified patterns across channels (email vs WhatsApp vs Web Form)
✅ You have a clear plan for transforming prototype → production

---

## Next Steps

Once Part 1 is complete, you'll move to Part 2: The Specialization Phase, where you'll:
- Transform your Python prototype into OpenAI Agents SDK implementation
- Build a real PostgreSQL database (using Neon DB)
- Create FastAPI endpoints for webhooks
- Build the complete Web Support Form in Next.js
- Deploy to Kubernetes with Kafka event streaming

Good luck with Part 1! 🚀
