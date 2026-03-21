# Context File Specifications

Detailed specifications for all required FTE context files.

## company-profile.md

### Required Sections

```markdown
# Company Profile - [Company Name]

## Company Overview
[One-paragraph description]

## Product Description
[Product name] helps [value prop] with:
- Feature 1
- Feature 2
- Feature 3
- Feature 4

## Target Customers
- Customer segment 1
- Customer segment 2
- Customer segment 3

## Brand Voice
- Characteristic 1
- Characteristic 2
- Characteristic 3
- Characteristic 4
```

### Minimum Fields
- Company name (title)
- Overview (1-2 paragraphs)
- Product name
- 3-5 key features
- 2-4 target customer segments
- 3-5 brand voice characteristics

## product-docs.md

### Required Sections

```markdown
# [Product Name] Documentation

## Core Features

### 1. [Feature Name]
[Description]
- Detail 1
- Detail 2
- Detail 3
- Detail 4

### 2. [Feature Name]
[Description...]

## Common Use Cases

### Use Case 1
[Description]

## Troubleshooting Guide

### Issue: [Problem Name]
**Solutions:**
1. Solution 1
2. Solution 2
3. Solution 3

## Pricing
- Plan 1: Price (details)
- Plan 2: Price (details)
- Plan 3: Price (details)
```

### Minimum Fields
- Product name (title)
- 3-5 core features with details
- 2-4 use cases
- 3-5 troubleshooting scenarios
- Pricing tiers

## sample-tickets.json

### Required Schema

```json
{
  "tickets": [
    {
      "id": 1,
      "channel": "email|whatsapp|web_form",
      "customer": {
        "email": "customer@example.com",
        "name": "Customer Name",
        "company": "Company Name"
      },
      "subject": "Subject line",
      "message": "Full customer message",
      "category": "technical|billing|feature_request|compliance|pricing|general",
      "priority": "low|medium|high|critical",
      "sentiment": "positive|neutral|negative"
    }
  ]
}
```

### Required Fields
- id: Unique integer
- channel: Must be email, whatsapp, or web_form
- customer: Object with identifying info
- message: String (full inquiry)
- category: Must be valid category
- priority: Must be valid priority
- sentiment: Must be valid sentiment

### Recommended Ticket Count
- Minimum: 5 tickets
- Recommended: 10+ tickets
- Distribution: Cover all channels and categories

## escalation-rules.md

### Required Structure

```markdown
# Escalation Rules

## Always Escalate to Human Support

1. **Billing Issues**
   - Refund requests
   - Payment disputes
   - Pricing negotiations

2. **Compliance & Legal**
   - HIPAA, GDPR, SOC2 requests
   - Legal questions

3. **High-Priority Technical Issues**
   - Urgent system outages
   - Data loss concerns

4. **Negative Sentiment**
   - Sentiment < 0.3
   - Multiple failed attempts

5. **Feature Requests**
   - All feature requests to product team

## Agent Can Handle

1. **Product Information**
   - Feature questions
   - How-to guidance

2. **General Support**
   - Account setup
   - Basic integration questions

3. **Bug Reporting**
   - Collect bug reports
   - Provide workarounds
```

### Minimum Categories
- At least 5 escalation triggers
- At least 3 agent-handled categories

## brand-voice.md

### Required Sections

```markdown
# Brand Voice Guidelines

## Tone
- **Characteristic 1:** Description
- **Characteristic 2:** Description
- **Characteristic 3:** Description
- **Characteristic 4:** Description

## Channel-Specific Guidelines

### Email (Gmail)
- Greeting: "[Format]"
- Closing: "[Format]"
- Length: [word range]
- Style: [Description]
- Signature: [Format]

### WhatsApp
- Greeting: "[Format]"
- Closing: "[Format]"
- Length: [char range]
- Style: [Description]

### Web Form
- Greeting: "[Format]"
- Closing: "[Format]"
- Length: [word range]
- Style: [Description]

## Phrases to Use
- "[Phrase 1]"
- "[Phrase 2]"
- "[Phrase 3]"

## Phrases to Avoid
- "[Phrase 1]" (Instead: "[Alternative]")
- "[Phrase 2]" (Instead: "[Alternative]")
```

### Minimum Fields
- 3-5 tone characteristics
- Guidelines for all 3 channels (email, whatsapp, web_form)
- 3-5 phrases to use
- 3-5 phrases to avoid with alternatives
