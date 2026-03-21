---
name: fte-context-generator
description: Generate all context files for Digital FTE prototypes. Use when starting a new FTE project or when company/product documentation needs to be created.
---

# FTE Context Generator

Generate knowledge base context files that power Digital FTE's understanding of company, product, and support policies.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing context files (if any), company documentation, product manuals |
| **Conversation** | Company name, industry, product features, target customers, support policies |
| **Skill References** | Context file structure, required fields, branding guidelines |
| **User Guidelines** | Company voice preferences, product naming, escalation triggers |

## Context Files Overview

The FTE requires 5 core context files:

1. **company-profile.md** - Company overview and brand identity
2. **product-docs.md** - Product features, use cases, troubleshooting
3. **sample-tickets.json** - Example customer inquiries across channels
4. **escalation-rules.md** - When to escalate vs. auto-resolve
5. **brand-voice.md** - Tone and communication style guidelines

## Generate Context Files

### 1. Company Profile

Create `context/company-profile.md`:

```markdown
# Company Profile - [Company Name]

## Company Overview
[One-paragraph description of what company does]

## Product Description
[Product name] helps businesses [core value proposition] with:
- [Feature 1]
- [Feature 2]
- [Feature 3]
- [Feature 4]

## Target Customers
- [Customer segment 1]
- [Customer segment 2]
- [Customer segment 3]

## Brand Voice
- [Tone characteristic 1]
- [Tone characteristic 2]
- [Tone characteristic 3]
- [Tone characteristic 4]
```

### 2. Product Documentation

Create `context/product-docs.md`:

```markdown
# [Product Name] Documentation

## Core Features

### 1. [Feature Name]
[Description of feature with key points]
- [Detail 1]
- [Detail 2]
- [Detail 3]
- [Detail 4]

### 2. [Feature Name]
[Description with details...]

## Common Use Cases

### Use Case 1
[Description of use case]

### Use Case 2
[Description of use case]

## Troubleshooting Guide

### Issue: [Problem Name]
**Solutions:**
1. [Solution 1]
2. [Solution 2]
3. [Solution 3]

### Issue: [Problem Name]
**Solutions:**
1. [Solution 1]
2. [Solution 2]

## Pricing
- [Plan 1]: [Price] ([details])
- [Plan 2]: [Price] ([details])
- [Plan 3]: [Price] ([details])
```

### 3. Sample Tickets

Create `context/sample-tickets.json`:

```json
{
  "tickets": [
    {
      "id": 1,
      "channel": "email",
      "customer": {
        "email": "customer@example.com",
        "name": "Customer Name",
        "company": "Company Name"
      },
      "subject": "Subject line",
      "message": "Full customer message",
      "category": "technical",
      "priority": "high",
      "sentiment": "negative"
    }
  ]
}
```

**Required Fields:**
- `id`: Unique ticket identifier
- `channel`: `email`, `whatsapp`, or `web_form`
- `customer`: Object with identifying info
- `message`: Full customer inquiry
- `category`: `technical`, `billing`, `feature_request`, `compliance`, `pricing`, or `general`
- `priority`: `low`, `medium`, `high`, or `critical`
- `sentiment`: `positive`, `neutral`, or `negative`

### 4. Escalation Rules

Create `context/escalation-rules.md`:

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

### 5. Brand Voice

Create `context/brand-voice.md`:

```markdown
# Brand Voice Guidelines

## Tone
- **[Characteristic 1]:** [Description]
- **[Characteristic 2]:** [Description]
- **[Characteristic 3]:** [Description]
- **[Characteristic 4]:** [Description]

## Channel-Specific Guidelines

### Email (Gmail)
- Greeting: "[Greeting format]"
- Closing: "[Closing format]"
- Length: [word range]
- Style: [Style description]
- Signature: [Signature format]

### WhatsApp
- Greeting: "[Greeting format]"
- Closing: "[Closing format]"
- Length: [character range]
- Style: [Style description]
- Quick responses preferred

### Web Form
- Greeting: "[Greeting format]"
- Closing: "[Closing format]"
- Length: [word range]
- Style: [Style description]
- Acknowledge receipt immediately

## Phrases to Use
- "[Phrase 1]"
- "[Phrase 2]"
- "[Phrase 3]"
- "[Phrase 4]"

## Phrases to Avoid
- "[Phrase 1]" (Instead: "[Alternative]")
- "[Phrase 2]" (Instead: "[Alternative]")
- "[Phrase 3]" (Instead: "[Alternative]")
```

## Context File Validation

After generating, validate each file:

```bash
# Check all files exist
ls context/*.md context/*.json

# Validate JSON syntax
python -m json.tool context/sample-tickets.json > /dev/null

# Check for required fields in tickets.json
jq '.tickets[] | has("id") and has("channel") and has("message")' context/sample-tickets.json
```

## Best Practices

1. **Be Specific**: Use actual product names, features, and company details
2. **Cover Edge Cases**: Include tickets for escalation scenarios
3. **Brand Consistency**: Ensure brand voice matches company identity
4. **Comprehensive Docs**: Include troubleshooting for common issues
5. **Test Data**: Ensure sample tickets reflect real customer inquiries

## Available Scripts

### generate_context.py
Interactive Python script that:
- Prompts for company information
- Creates company-profile.md with user input
- Creates product-docs.md template
- Creates sample-tickets.json with example ticket
- Creates escalation-rules.md with standard rules
- Creates brand-voice.md based on company info

**Usage:**
```bash
python scripts/generate_context.py
```

**Interactive Prompts:**
- Company name
- Company overview
- Product name and value proposition
- Key features
- Target customers
- Brand voice characteristics

### assets/ directory structure
```
fte-context-generator/
├── SKILL.md                          # Main skill documentation
├── scripts/
│   └── generate_context.py             # Interactive context generator
├── assets/
│   └── company-profile-template.md      # Manual template
└── references/
    └── context-file-specs.md          # Detailed specifications
```

## Next Steps

After creating context files:
1. Build agent prototype using `fte-prototype-agent` skill
2. Test agent with sample tickets to verify context understanding
3. Refine context based on agent performance
