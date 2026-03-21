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
        result = agent.analyze_sentiment("How does this work?")
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
