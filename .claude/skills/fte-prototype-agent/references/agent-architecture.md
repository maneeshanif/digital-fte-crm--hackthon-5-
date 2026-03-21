# FTE Agent Architecture

Complete architecture reference for the Customer Success Agent.

## Core Components

```
CustomerAgent
├── Knowledge Base (product-docs.md)
├── Conversation Memory (dict)
├── Sentiment History (dict)
├── Methods:
│   ├── load_knowledge_base()
│   ├── process_message()
│   ├── analyze_sentiment()
│   ├── determine_priority()
│   ├── search_knowledge_base()
│   ├── generate_response()
│   ├── check_escalation()
│   ├── detect_category()
│   └── store_conversation()
└── Helpers:
    ├── _get_greeting()
    ├── _build_response_body()
    ├── _get_closing()
    └── _get_escalation_note()
```

## Data Flow

```
1. Customer Message
   ↓
2. Sentiment Analysis
   ↓
3. Priority Determination
   ↓
4. Knowledge Base Search
   ↓
5. Response Generation
   ↓
6. Escalation Check
   ↓
7. Store Conversation
   ↓
8. Return Response + Metadata
```

## Enums

### Channel
```python
class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"
```

### Sentiment
```python
class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
```

### Priority
```python
class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

## Return Structure

```python
{
    "response": "Generated response text",
    "sentiment": "positive|neutral|negative",
    "should_escalate": True|False,
    "escalation_reason": "Reason for escalation (or empty)",
    "priority": "low|medium|high|critical",
    "category": "technical|billing|feature_request|compliance|pricing|general"
}
```

## Sentiment Detection Logic

### Positive Indicators
- "love", "amazing", "great", "excellent", "happy"
- "thanks", "thank you", "helpful", "appreciate"

### Negative Indicators
- "angry", "frustrated", "hate", "terrible", "worst"
- "losing patience", "waste of time", "useless"
- "refund", "cancel", "threaten", "lawsuit"

### Decision Logic
```python
if negative_count > positive_count:
    return Sentiment.NEGATIVE
elif positive_count > negative_count:
    return Sentiment.POSITIVE
else:
    return Sentiment.NEUTRAL
```

## Priority Determination Logic

### Critical Keywords
- "urgent", "asap", "emergency", "critical", "immediately"
- "system down", "outage", "cannot login", "losing money"

### Decision Logic
```python
if any(urgent_keyword in message):
    return Priority.CRITICAL
elif sentiment == NEGATIVE:
    return Priority.HIGH
elif '?' in message:
    return Priority.MEDIUM
else:
    return Priority.LOW
```

## Escalation Rules

### Always Escalate
1. Sentiment == NEGATIVE
2. Billing keywords present (refund, payment, pricing, discount, negotiate)
3. Compliance keywords present (hipaa, gdpr, soc2, legal, compliance, baa)
4. Priority == CRITICAL
5. Category == feature_request

### Never Escalate
- General product questions with neutral/positive sentiment
- How-to guidance requests
- Basic integration questions

## Category Detection

### Keywords Mapping
```python
{
    "technical": ["workflow", "integration", "api", "bug", "error", "login"],
    "billing": ["refund", "payment", "price", "invoice", "billing"],
    "feature_request": ["feature", "add", "support", "can you", "would be great"],
    "compliance": ["security", "hipaa", "gdpr", "soc2", "compliance"],
    "pricing": ["how much", "cost", "pricing", "license", "subscription"]
}
```

## Response Generation

### Channel-Specific Formatting

| Channel | Greeting | Closing | Max Length | Style |
|---------|----------|---------|------------|-------|
| Email | "Dear [Name]" | "Best regards,\\nTeam" | 500 words | Formal, detailed |
| WhatsApp | "Hi [Name]!" | "Let me know if you need more help!" | 160 chars | Conversational, emojis |
| Web Form | "Hello [Name]," | "We'll get back to you shortly!" | 300 words | Semi-formal |

## Memory Structure

```python
conversation_memory = {
    "customer_id@example.com": [
        {
            "message": "Customer message",
            "response": "Agent response",
            "channel": "email",
            "sentiment": "neutral",
            "timestamp": "2024-03-14 10:00:00"
        }
    ]
}

customer_sentiment_history = {
    "customer_id@example.com": [
        {"sentiment": "neutral", "timestamp": "2024-03-14 10:00:00"},
        {"sentiment": "positive", "timestamp": "2024-03-14 10:05:00"}
    ]
}
```

## Performance Targets

| Metric | Target | Prototype |
|--------|--------|-----------|
| Response Time (Email) | < 2.0s | TBD |
| Response Time (WhatsApp) | < 1.0s | TBD |
| KB Search Time | < 0.5s | TBD |
| Sentiment Accuracy | > 80% | TBD |
| Escalation Accuracy | > 90% | TBD |
