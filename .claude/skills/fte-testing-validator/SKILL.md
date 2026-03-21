---
name: fte-testing-validator
description: Test and validate FTE prototype with performance metrics and edge case coverage. Use when validating prototype quality or preparing for production transition.
---

# FTE Testing Validator

Test and validate the FTE prototype to ensure it meets quality standards before moving to production.

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Agent implementation, MCP server, test files |
| **Conversation** | Testing requirements, performance targets, edge case priorities |
| **Skill References** | Testing frameworks, validation criteria, metrics collection |
| **User Guidelines** | Acceptance criteria, reporting format preferences |

## Validation Overview

Testing covers:

1. **Functional Tests** - Verify all agent capabilities work
2. **Integration Tests** - Test MCP server tools
3. **Performance Tests** - Measure response times and accuracy
4. **Edge Cases** - Handle unusual scenarios gracefully
5. **Documentation** - Record findings and performance baselines

## Test Structure

```
tests/
├── test_agent.py          # Agent functionality tests
├── test_mcp_server.py     # MCP server tool tests
├── test_edge_cases.py      # Edge case scenarios
├── test_performance.py      # Performance benchmarks
└── fixtures/
    ├── sample_tickets.json  # Test data
    └── expected_outputs.json # Expected results
```

## Create Test Suite

### 1. Agent Functional Tests

Create `tests/test_agent.py`:

```python
import pytest
from agent.customer_agent import CustomerAgent, Channel, Sentiment, Priority

@pytest.fixture
def agent():
    """Fixture providing initialized agent"""
    return CustomerAgent()

class TestAgentBasics:
    """Test basic agent functionality"""

    def test_sentiment_positive(self, agent):
        """Test positive sentiment detection"""
        result = agent.analyze_sentiment("I love this product!")
        assert result == Sentiment.POSITIVE

    def test_sentiment_negative(self, agent):
        """Test negative sentiment detection"""
        result = agent.analyze_sentiment("I'm very frustrated and hate this")
        assert result == Sentiment.NEGATIVE

    def test_sentiment_neutral(self, agent):
        """Test neutral sentiment detection"""
        result = agent.analyze_sentiment("How do I use this feature?")
        assert result == Sentiment.NEUTRAL

    def test_priority_critical(self, agent):
        """Test critical priority detection"""
        result = agent.determine_priority("URGENT system down!", Sentiment.NEUTRAL)
        assert result == Priority.CRITICAL

    def test_priority_high_negative(self, agent):
        """Test high priority for negative sentiment"""
        result = agent.determine_priority("Not working well", Sentiment.NEGATIVE)
        assert result == Priority.HIGH

    def test_knowledge_search(self, agent):
        """Test knowledge base search"""
        results = agent.search_knowledge_base("Slack integration")
        assert len(results) > 0
        assert any("Slack" in result for result in results)

    def test_escalation_billing(self, agent):
        """Test escalation for billing issues"""
        should_escalate, reason = agent.check_escalation(
            message="I want a refund",
            sentiment=Sentiment.NEUTRAL,
            priority=Priority.MEDIUM,
            category="billing"
        )
        assert should_escalate == True
        assert "billing" in reason.lower()

    def test_escalation_negative_sentiment(self, agent):
        """Test escalation for negative sentiment"""
        should_escalate, reason = agent.check_escalation(
            message="This is terrible",
            sentiment=Sentiment.NEGATIVE,
            priority=Priority.MEDIUM,
            category="general"
        )
        assert should_escalate == True
        assert "negative" in reason.lower()

    def test_no_escalation_general(self, agent):
        """Test no escalation for general inquiries"""
        should_escalate, reason = agent.check_escalation(
            message="How do I use feature X?",
            sentiment=Sentiment.NEUTRAL,
            priority=Priority.MEDIUM,
            category="general"
        )
        assert should_escalate == False
        assert reason == ""

class TestAgentIntegration:
    """Test agent end-to-end processing"""

    def test_email_processing(self, agent):
        """Test processing email message"""
        result = agent.process_message(
            message="How do I connect my Slack workspace?",
            channel=Channel.EMAIL,
            customer_name="John Doe",
            customer_id="john@example.com"
        )

        assert result['sentiment'] in [Sentiment.POSITIVE, Sentiment.NEUTRAL]
        assert result['priority'] in [Priority.LOW, Priority.MEDIUM]
        assert 'response' in result
        assert len(result['response']) > 0

    def test_whatsapp_processing(self, agent):
        """Test processing WhatsApp message"""
        result = agent.process_message(
            message="Hi! Quick question",
            channel=Channel.WHATSAPP,
            customer_name="Jane Smith"
        )

        assert result['sentiment'] in [Sentiment.POSITIVE, Sentiment.NEUTRAL]
        assert result['priority'] == Priority.LOW
        assert len(result['response']) <= 300  # WhatsApp is shorter

    def test_web_form_processing(self, agent):
        """Test processing web form submission"""
        result = agent.process_message(
            message="Feature request please",
            channel=Channel.WEB_FORM,
            customer_name="Bob Johnson"
        )

        assert result['should_escalate'] == True  # Feature requests escalate
        assert "feature" in result['escalation_reason'].lower()

    def test_conversation_memory(self, agent):
        """Test conversation is stored in memory"""
        customer_id = "test@example.com"

        agent.process_message(
            message="First question",
            channel=Channel.EMAIL,
            customer_id=customer_id
        )

        history = agent.get_customer_history(customer_id)

        assert len(history) == 1
        assert history[0]['message'] == "First question"
```

### 2. MCP Server Tests

Create `tests/test_mcp_server.py`:

```python
import pytest
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
import asyncio

@pytest.fixture
async def mcp_session():
    """Fixture providing MCP server session"""
    async with stdio_client() as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

@pytest.mark.asyncio
class TestMCPTools:
    """Test MCP server tools"""

    async def test_list_tools(self, mcp_session):
        """Test that all tools are available"""
        tools = await mcp_session.list_tools()

        tool_names = [tool.name for tool in tools]

        expected_tools = [
            'search_knowledge_base',
            'create_ticket',
            'get_customer_history',
            'send_response',
            'escalate_to_human',
            'analyze_sentiment',
            'get_channel_formatting'
        ]

        for tool in expected_tools:
            assert tool in tool_names, f"Missing tool: {tool}"

    async def test_search_knowledge_base(self, mcp_session):
        """Test knowledge base search tool"""
        result = await mcp_session.call_tool(
            "search_knowledge_base",
            {"query": "Slack integration"}
        )

        assert isinstance(result, str)
        assert "Slack" in result or "integration" in result.lower()

    async def test_analyze_sentiment_positive(self, mcp_session):
        """Test sentiment analysis for positive message"""
        result = await mcp_session.call_tool(
            "analyze_sentiment",
            {"message": "I love this product!"}
        )

        data = json.loads(result)
        assert data['sentiment'] == 'positive'
        assert 'recommendation' in data

    async def test_analyze_sentiment_negative(self, mcp_session):
        """Test sentiment analysis for negative message"""
        result = await mcp_session.call_tool(
            "analyze_sentiment",
            {"message": "I'm very frustrated with this"}
        )

        data = json.loads(result)
        assert data['sentiment'] == 'negative'
        assert 'empathy' in data['recommendation'].lower()

    async def test_create_ticket(self, mcp_session):
        """Test ticket creation"""
        result = await mcp_session.call_tool(
            "create_ticket",
            {
                "customer_id": "test@example.com",
                "issue": "Test issue",
                "priority": "high",
                "channel": "email"
            }
        )

        data = json.loads(result)
        assert 'ticket_id' in data
        assert data['status'] == 'created'
        assert data['customer_id'] == 'test@example.com'

    async def test_get_channel_formatting(self, mcp_session):
        """Test channel formatting guidelines"""
        result = await mcp_session.call_tool(
            "get_channel_formatting",
            {"channel": "whatsapp"}
        )

        data = json.loads(result)
        assert 'greeting' in data
        assert 'closing' in data
        assert 'max_length' in data
        assert data['emojis_allowed'] == True
```

### 3. Edge Case Tests

Create `tests/test_edge_cases.py`:

```python
import pytest
from agent.customer_agent import CustomerAgent, Channel

@pytest.fixture
def agent():
    return CustomerAgent()

class TestEdgeCases:
    """Test edge cases and unusual scenarios"""

    def test_empty_message(self, agent):
        """Test handling of empty message"""
        result = agent.process_message(
            message="",
            channel=Channel.EMAIL
        )
        # Should handle gracefully, not crash

    def test_very_long_message(self, agent):
        """Test handling of very long message"""
        long_message = "Test " * 10000  # Very long

        result = agent.process_message(
            message=long_message,
            channel=Channel.EMAIL
        )
        # Should handle without errors

    def test_multiple_questions(self, agent):
        """Test message with multiple questions"""
        result = agent.process_message(
            message="How do I use Slack? What about Gmail? Is there API support?",
            channel=Channel.EMAIL
        )
        # Should handle multiple questions

    def test_escalation_trigger_combination(self, agent):
        """Test escalation with multiple triggers"""
        result = agent.process_message(
            message="I want a refund for this terrible service!",
            channel=Channel.EMAIL
        )
        assert result['should_escalate'] == True
        assert result['priority'] == Priority.HIGH

    def test_channel_switching(self, agent):
        """Test same customer on different channels"""
        customer_id = "multi-channel@example.com"

        # Email first
        agent.process_message(
            message="Email question",
            channel=Channel.EMAIL,
            customer_id=customer_id
        )

        # Then WhatsApp
        result = agent.process_message(
            message="WhatsApp question",
            channel=Channel.WHATSAPP,
            customer_id=customer_id
        )

        # Should maintain history across channels
        history = agent.get_customer_history(customer_id)
        assert len(history) == 2

    def test_unknown_channel(self, agent):
        """Test handling of unknown channel"""
        try:
            Channel("unknown")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected

    def test_unicode_message(self, agent):
        """Test handling of unicode characters"""
        result = agent.process_message(
            message="Hello 世界 🌍! How are you?",
            channel=Channel.EMAIL
        )
        # Should handle unicode without errors

    def test_special_characters(self, agent):
        """Test handling of special characters"""
        result = agent.process_message(
            message="Test with <>&\"' characters",
            channel=Channel.EMAIL
        )
        # Should handle special characters safely
```

### 4. Performance Tests

Create `tests/test_performance.py`:

```python
import pytest
import time
from agent.customer_agent import CustomerAgent, Channel

@pytest.fixture
def agent():
    return CustomerAgent()

class TestPerformance:
    """Test performance characteristics"""

    def test_response_time_email(self, agent):
        """Test response time for email"""
        start = time.time()

        agent.process_message(
            message="How do I integrate Slack?",
            channel=Channel.EMAIL
        )

        elapsed = time.time() - start

        # Should be fast (adjust threshold as needed)
        assert elapsed < 2.0, f"Response too slow: {elapsed:.2f}s"

    def test_response_time_whatsapp(self, agent):
        """Test response time for WhatsApp"""
        start = time.time()

        agent.process_message(
            message="Quick question?",
            channel=Channel.WHATSAPP
        )

        elapsed = time.time() - start

        # WhatsApp should be faster
        assert elapsed < 1.0, f"WhatsApp response too slow: {elapsed:.2f}s"

    def test_knowledge_search_performance(self, agent):
        """Test knowledge base search performance"""
        start = time.time()

        agent.search_knowledge_base("API integration documentation")

        elapsed = time.time() - start

        assert elapsed < 0.5, f"KB search too slow: {elapsed:.2f}s"

    def test_memory_usage(self, agent):
        """Test memory usage with many conversations"""
        import sys
        import gc

        initial_size = sys.getsizeof(agent.conversation_memory)

        # Create many conversations
        for i in range(100):
            agent.process_message(
                message=f"Test message {i}",
                channel=Channel.EMAIL,
                customer_id=f"user{i}@example.com"
            )

        final_size = sys.getsizeof(agent.conversation_memory)

        # Should not grow unreasonably
        growth_factor = final_size / initial_size if initial_size > 0 else 1
        assert growth_factor < 100, f"Memory growth too high: {growth_factor}x"
```

## Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_agent.py -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run performance tests only
uv run pytest tests/test_performance.py -v
```

## Validation Checklist

### Functional Validation
- [ ] All agent methods execute without errors
- [ ] Sentiment analysis detects positive/neutral/negative correctly
- [ ] Priority determination matches expected logic
- [ ] Knowledge base search returns relevant results
- [ ] Escalation logic follows rules from context files
- [ ] Response generation produces channel-appropriate output

### MCP Server Validation
- [ ] All 7 tools are accessible
- [ ] Tools return expected data structures
- [ ] Tool documentation is clear and accurate
- [ ] Server handles concurrent requests
- [ ] Error handling is graceful

### Performance Validation
- [ ] Response time < 2s for email
- [ ] Response time < 1s for WhatsApp
- [ ] Knowledge base search < 0.5s
- [ ] Memory usage is reasonable

### Edge Case Validation
- [ ] Empty messages handled gracefully
- [ ] Very long messages processed correctly
- [ ] Multiple questions in one message handled
- [ ] Unicode characters supported
- [ ] Special characters handled safely
- [ ] Channel switching maintains history

## Performance Baselines

Record these metrics after testing:

```python
# tests/baseline.py
BASELINE = {
    "average_response_time": {
        "email": 1.2,  # seconds
        "whatsapp": 0.3,
        "web_form": 0.8
    },
    "accuracy": {
        "sentiment_analysis": 0.85,
        "priority_determination": 0.90,
        "escalation_decision": 0.95
    },
    "escalation_rate": 0.25,  # 25% of tickets escalate
    "knowledge_base_hit_rate": 0.80  # 80% find relevant docs
}

# Save baseline
import json
with open('tests/baseline.json', 'w') as f:
    json.dump(BASELINE, f, indent=2)
```

## Validation Report

Create `tests/validation_report.md`:

```markdown
# FTE Prototype Validation Report

## Test Results

### Functional Tests
- **Tests Run**: 15
- **Passed**: 14
- **Failed**: 1
- **Success Rate**: 93.3%

### Performance Tests
- **Average Response Time**: 1.1s
- **Target**: < 2.0s
- **Status**: ✅ PASSED

### Edge Case Tests
- **Tests Run**: 8
- **Passed**: 8
- **Failed**: 0
- **Success Rate**: 100%

## Performance Baselines

| Metric | Value | Target | Status |
|--------|--------|--------|--------|
| Email Response Time | 1.2s | < 2.0s | ✅ |
| WhatsApp Response Time | 0.3s | < 1.0s | ✅ |
| KB Search Time | 0.2s | < 0.5s | ✅ |
| Sentiment Accuracy | 85% | > 80% | ✅ |
| Escalation Accuracy | 95% | > 90% | ✅ |

## Issues Found

1. **Issue**: Knowledge base returns irrelevant results for vague queries
   - **Impact**: Medium
   - **Recommendation**: Improve query expansion in search

## Recommendations

1. Ready for Part 2 transition
2. Consider adding more sophisticated sentiment analysis
3. Implement vector similarity search for knowledge base

## Conclusion

Prototype meets validation criteria and is ready for production transition.
```

## Available Scripts

### run_tests.py
Comprehensive test runner that:
- Executes all test suites sequentially
- Captures test results and timings
- Generates HTML validation report
- Creates JSON results for programmatic access
- Calculates success rate and coverage metrics

**Usage:**
```bash
python scripts/run_tests.py
```

**What It Does:**
1. Runs agent functional tests
2. Runs MCP server tests
3. Runs edge case tests
4. Runs performance tests
5. Runs all tests with coverage
6. Generates `tests/validation_report.md`
7. Creates `tests/validation_results.json`

**Report Sections:**
- Test summary (total, passed, failed, success rate)
- Individual test results with status
- Performance baseline comparisons
- Issues found with recommendations
- Overall readiness assessment

### references/ directory structure
```
fte-testing-validator/
├── SKILL.md                          # Main skill documentation
├── scripts/
│   └── run_tests.py                   # Automated test runner
└── references/
    └── test-coverage-baseline.md       # Coverage and performance targets
```

## Next Steps

After validation:
1. Document all findings in validation report
2. Address any critical issues found
3. Prepare transition plan to Part 2 (Specialization)
