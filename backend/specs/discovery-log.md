# Discovery Log

Date: 2024-03-14

## Requirements Discovered

### Agent Capabilities
- Sentiment analysis (keyword-based)
- Priority determination (low/medium/high/critical)
- Knowledge base search (keyword overlap)
- Response generation (channel-specific)
- Escalation logic (billing, compliance, sentiment, critical, feature requests)
- Conversation memory (in-memory)
- Category detection (5 categories)

### MCP Server
- 7 tools implemented
- FastMCP framework used
- stdio transport
- Tool descriptions and parameter validation

### Context Files
- company-profile.md (TechFlow SaaS)
- product-docs.md (TechFlow features, use cases, troubleshooting, pricing)
- sample-tickets.json (10 example tickets across channels)
- escalation-rules.md (5 escalation triggers, 3 agent-handled categories)
- brand-voice.md (Tone guidelines for 3 channels)

### Technical Decisions
- Python 3.14.3 (via uv)
- uv package manager (fast installation)
- FastMCP for tool exposure
- In-memory storage for prototype
- No external databases (Part 2 will add PostgreSQL)

### Edge Cases Handled
- Empty messages
- Very long messages
- Multiple questions in one message
- Channel switching mid-conversation
- Unknown channel values
- Unicode characters
- Negative sentiment
- Critical priority
- Feature requests

## Questions for Part 2
1. Should sentiment analysis use LLM instead of keywords?
2. Should knowledge base use vector search instead of keyword overlap?
3. Should escalation logic be more sophisticated?
4. Should conversation memory be persistent (database)?
5. Should response generation use LLM instead of templates?
6. Should category detection use ML classification?

## Performance Baseline
To be established after testing:
- Response time per channel
- Sentiment analysis accuracy
- KB search hit rate
- Escalation accuracy
