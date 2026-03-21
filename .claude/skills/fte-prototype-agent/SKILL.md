---
name: fte-prototype-agent
description: Build core customer agent prototype with sentiment analysis, knowledge base search, and response generation. Use when creating initial FTE prototype or when implementing agent capabilities.
---

# FTE Prototype Agent

Build a working Customer Success Agent prototype that processes customer messages across channels with sentiment awareness and escalation logic.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing agent files, context files directory structure |
| **Conversation** | Agent behavior preferences, sentiment thresholds, escalation rules |
| **Skill References** | Agent class structure, method signatures, enums |
| **User Guidelines** | Performance requirements, logging preferences, error handling approach |

## Agent Architecture

The prototype agent implements:

1. **Channel Normalization** - Handle email, WhatsApp, web form uniformly
2. **Sentiment Analysis** - Detect positive/neutral/negative sentiment
3. **Priority Determination** - Classify urgency (low/medium/high/critical)
4. **Knowledge Base Search** - Find relevant product documentation
5. **Response Generation** - Create channel-appropriate responses
6. **Escalation Decision** - Identify when to route to humans
7. **Conversation Memory** - Track interaction history

## Create Agent Implementation

### File Structure

```
src/agent/
├── customer_agent.py     # Main agent class
├── tools.py              # Agent tools (knowledge search, sentiment)
├── prompts.py            # Response generation prompts
├── formatter.py          # Channel-specific formatting
└── sentiment.py          # Sentiment analysis logic
```

### Core Agent Class

Create `src/agent/customer_agent.py`:

```python
from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime
from collections import defaultdict

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
        self.conversation_memory = defaultdict(list)
        self.customer_sentiment_history = defaultdict(list)

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

        Returns Dict with:
        - response: Generated response text
        - sentiment: Customer sentiment
        - should_escalate: Whether to escalate to human
        - escalation_reason: Reason for escalation
        - priority: Ticket priority
        - category: Inquiry category
        """
        # Analyze sentiment
        sentiment = self.analyze_sentiment(message)

        # Determine priority
        priority = self.determine_priority(message, sentiment)

        # Search knowledge base
        relevant_docs = self.search_knowledge_base(message)

        # Generate response
        response = self.generate_response(
            message=message,
            relevant_docs=relevant_docs,
            channel=channel,
            customer_name=customer_name,
            sentiment=sentiment
        )

        # Check escalation
        should_escalate, escalation_reason = self.check_escalation(
            message=message,
            sentiment=sentiment,
            priority=priority,
            category=self.detect_category(message)
        )

        # Store conversation
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
```

### Key Methods Implementation

#### Sentiment Analysis

```python
def analyze_sentiment(self, message: str) -> Sentiment:
    """Simple keyword-based sentiment analysis"""
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
```

#### Priority Determination

```python
def determine_priority(self, message: str, sentiment: Sentiment) -> Priority:
    """Determine ticket priority"""
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
```

#### Knowledge Base Search

```python
def search_knowledge_base(self, query: str) -> List[str]:
    """Keyword-based search of product documentation"""
    import re

    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))

    sections = self.knowledge_base.split('\n## ')
    scored_sections = []

    for section in sections:
        section_lower = section.lower()
        section_words = set(re.findall(r'\w+', section_lower))
        overlap = len(query_words & section_words)

        if overlap > 0:
            scored_sections.append((section, overlap))

    scored_sections.sort(key=lambda x: x[1], reverse=True)
    return [section[0] for section in scored_sections[:3]]
```

#### Escalation Check

```python
def check_escalation(
    self,
    message: str,
    sentiment: Sentiment,
    priority: Priority,
    category: str
) -> tuple[bool, str]:
    """Check if ticket should escalate to human"""
    # Load escalation rules
    with open('context/escalation-rules.md', 'r') as f:
        escalation_rules = f.read()

    # Negative sentiment
    if sentiment == Sentiment.NEGATIVE:
        return True, "Negative customer sentiment detected"

    # Billing issues
    billing_keywords = ['refund', 'payment', 'pricing', 'discount', 'negotiate']
    if any(kw in message.lower() for kw in billing_keywords):
        return True, "Billing/pricing related inquiry"

    # Compliance/legal
    compliance_keywords = ['hipaa', 'gdpr', 'soc2', 'legal', 'compliance', 'baa']
    if any(kw in message.lower() for kw in compliance_keywords):
        return True, "Compliance/legal inquiry"

    # Critical priority
    if priority == Priority.CRITICAL:
        return True, "Critical priority issue"

    # Feature requests
    if category == "feature_request":
        return True, "Feature request - needs product team review"

    return False, ""
```

### Test Agent

Create `tests/test_agent.py`:

```python
from agent.customer_agent import CustomerAgent, Channel, Sentiment, Priority

def test_basic_processing():
    agent = CustomerAgent()

    result = agent.process_message(
        message="How do I connect my Slack workspace?",
        channel=Channel.WHATSAPP,
        customer_name="Sarah Chen"
    )

    assert result['sentiment'] == Sentiment.POSITIVE
    assert result['priority'] == Priority.MEDIUM
    assert 'Slack' in result['response']
    print("Test passed!")

if __name__ == "__main__":
    test_basic_processing()
```

## Edge Case Handling

### Empty Messages
```python
if not message or not message.strip():
    return {"error": "Empty message received"}
```

### Very Long Messages
```python
MAX_MESSAGE_LENGTH = 10000
if len(message) > MAX_MESSAGE_LENGTH:
    message = message[:MAX_MESSAGE_LENGTH] + "... (truncated)"
```

### Multiple Questions
```python
questions = [q.strip() for q in message.split('?') if q.strip()]
if len(questions) > 1:
    # Process each question separately or combine responses
```

### Unknown Channels
```python
try:
    channel = Channel(channel_input)
except ValueError:
    return {"error": f"Unknown channel: {channel_input}"}
```

## Performance Optimization

1. **Cache Knowledge Base**: Load once at initialization
2. **Precompute Keywords**: Compile regex patterns for common searches
3. **Batch Processing**: Process multiple messages efficiently
4. **Async I/O**: Use async for external API calls (future production)

## Available Scripts

### scaffold_agent.py
Automated script that creates:
- Complete `src/agent/` directory structure
- Main `customer_agent.py` with all methods implemented
- Submodule files (`tools.py`, `prompts.py`, `formatter.py`, `sentiment.py`)
- `tests/test_agent.py` with basic test cases
- All necessary `__init__.py` files

**Usage:**
```bash
python scripts/scaffold_agent.py
```

**What It Creates:**
- Agent class with 7 core methods
- Sentiment, priority, and escalation logic
- Knowledge base search functionality
- Channel-specific response generation
- Conversation memory management
- Test suite with pytest fixtures

### assets/ directory structure
```
fte-prototype-agent/
├── SKILL.md                          # Main skill documentation
├── scripts/
│   └── scaffold_agent.py              # Automated agent scaffolding
├── assets/
│   └── agent-template.py              # Customizable agent template
└── references/
    └── agent-architecture.md           # Complete architecture reference
```

## Next Steps

After agent prototype:
1. Create MCP server using `fte-mcp-server` skill
2. Test with sample tickets from context files
3. Validate escalation logic
