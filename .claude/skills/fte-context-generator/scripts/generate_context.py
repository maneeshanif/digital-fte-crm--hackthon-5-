#!/usr/bin/env python3
"""
Generate FTE Context Files
Interactive script to create all required context files for FTE prototype
"""

import json
import os
from pathlib import Path


def create_context_files():
    """Generate all context files from user input"""

    print("=== FTE Context Files Generator ===\n")

    # 1. Company Profile
    print("Creating context/company-profile.md...")
    profile = {
        "company_name": input("Company name: "),
        "overview": input("Company overview (one paragraph): "),
        "product_name": input("Product name: "),
        "product_description": input("Product value proposition: "),
        "features": input("Key features (comma-separated): ").split(","),
        "target_customers": input("Target customers (comma-separated): ").split(","),
        "brand_voice": [
            input("Brand voice characteristic 1: "),
            input("Brand voice characteristic 2: "),
            input("Brand voice characteristic 3: ")
        ]
    }

    company_profile = f"""# Company Profile - {profile['company_name']}

## Company Overview
{profile['overview']}

## Product Description
{profile['product_name']} helps businesses {profile['product_description']} with:
"""

    for feature in profile['features']:
        company_profile += f"- {feature.strip()}\n"

    company_profile += f"""
## Target Customers
"""

    for customer in profile['target_customers']:
        company_profile += f"- {customer.strip()}\n"

    company_profile += """
## Brand Voice
"""

    for i, voice in enumerate(profile['brand_voice'], 1):
        company_profile += f"- {voice}\n"

    Path("context/company-profile.md").write_text(company_profile)

    # 2. Product Docs
    print("\nCreating context/product-docs.md...")
    print("(This will create a template. Edit manually for full details)")
    product_docs = f"""# {profile['product_name']} Documentation

## Core Features

### 1. [Feature Name]
[Description of feature with key points]
- [Detail 1]
- [Detail 2]
- [Detail 3]

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
"""
    Path("context/product-docs.md").write_text(product_docs)

    # 3. Sample Tickets
    print("\nCreating context/sample-tickets.json...")
    print("(This creates template tickets. Add real examples later)")
    sample_tickets = {
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
    Path("context/sample-tickets.json").write_text(
        json.dumps(sample_tickets, indent=2)
    )

    # 4. Escalation Rules
    print("\nCreating context/escalation-rules.md...")
    escalation_rules = """# Escalation Rules

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
"""
    Path("context/escalation-rules.md").write_text(escalation_rules)

    # 5. Brand Voice
    print("\nCreating context/brand-voice.md...")
    brand_voice = f"""# Brand Voice Guidelines

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
- Signature: Include "{profile['company_name']} Support Team"

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
"""
    Path("context/brand-voice.md").write_text(brand_voice)

    print("\n✅ All context files created!")
    print("\nNext steps:")
    print("  1. Edit context/product-docs.md with actual product details")
    print("  2. Add more sample tickets to context/sample-tickets.json")
    print("  3. Customize escalation rules and brand voice as needed")


if __name__ == "__main__":
    # Ensure context directory exists
    Path("context").mkdir(exist_ok=True)

    create_context_files()
