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
- Formatted response appropriate for channel

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
- `customer_id`: Unique customer identifier
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
- Web Form → Email + API response
