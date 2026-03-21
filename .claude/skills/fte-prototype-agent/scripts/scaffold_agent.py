#!/usr/bin/env python3
"""
Scaffold FTE Agent Files
Create all necessary files for the customer agent prototype
"""

from pathlib import Path


def create_agent_structure():
    """Create complete agent file structure"""

    print("=== FTE Agent Scaffold ===\n")

    # Create src/agent directory structure
    agent_dir = Path("src/agent")
    agent_dir.mkdir(parents=True, exist_ok=True)

    # 1. __init__.py
    print("Creating src/agent/__init__.py...")
    (agent_dir / "__init__.py").write_text("""
from .customer_agent import CustomerAgent, Channel, Sentiment, Priority

__all__ = ['CustomerAgent', 'Channel', 'Sentiment', 'Priority']
""")

    # 2. customer_agent.py
    print("Creating src/agent/customer_agent.py...")
    (agent_dir / "customer_agent.py").write_text("""
from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime
from collections import defaultdict
import re

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
    \"\"\"Prototype Customer Success Agent\"\"\"

    def __init__(self):
        self.load_knowledge_base()
        self.conversation_memory = defaultdict(list)
        self.customer_sentiment_history = defaultdict(list)

    def load_knowledge_base(self):
        \"\"\"Load product documentation from context folder\"\"\"
        with open('context/product-docs.md', 'r') as f:
            self.knowledge_base = f.read()

    def analyze_sentiment(self, message: str) -> Sentiment:
        \"\"\"Simple keyword-based sentiment analysis\"\"\"
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
        \"\"\"Determine ticket priority based on content and sentiment\"\"\"
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
        \"\"\"Simple keyword-based search of product documentation\"\"\"
        query_lower = query.lower()
        query_words = set(re.findall(r'\\w+', query_lower))

        sections = self.knowledge_base.split('\\n## ')
        scored_sections = []

        for section in sections:
            section_lower = section.lower()
            section_words = set(re.findall(r'\\w+', section_lower))
            overlap = len(query_words & section_words)

            if overlap > 0:
                scored_sections.append((section, overlap))

        scored_sections.sort(key=lambda x: x[1], reverse=True)
        return [section[0] for section in scored_sections[:3]]

    def check_escalation(
        self,
        message: str,
        sentiment: Sentiment,
        priority: Priority,
        category: str
    ) -> tuple[bool, str]:
        \"\"\"Check if this should be escalated to human support\"\"\"
        with open('context/escalation-rules.md', 'r') as f:
            escalation_rules = f.read()

        if sentiment == Sentiment.NEGATIVE:
            return True, "Negative customer sentiment detected"

        billing_keywords = ['refund', 'payment', 'pricing', 'discount', 'negotiate']
        if any(kw in message.lower() for kw in billing_keywords):
            return True, "Billing/pricing related inquiry"

        compliance_keywords = ['hipaa', 'gdpr', 'soc2', 'legal', 'compliance', 'baa']
        if any(kw in message.lower() for kw in compliance_keywords):
            return True, "Compliance/legal inquiry"

        if priority == Priority.CRITICAL:
            return True, "Critical priority issue"

        if category == "feature_request":
            return True, "Feature request - needs product team review"

        return False, ""

    def detect_category(self, message: str) -> str:
        \"\"\"Detect the category of the customer's inquiry\"\"\"
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
        \"\"\"Store conversation in memory\"\"\"
        self.conversation_memory[customer_id].append({
            "message": message,
            "response": response,
            "channel": channel,
            "sentiment": sentiment,
            "timestamp": str(datetime.now())
        })

    def get_customer_history(self, customer_id: str) -> List[Dict]:
        \"\"\"Get conversation history for a customer\"\"\"
        return self.conversation_memory.get(customer_id, [])

    def generate_response(
        self,
        message: str,
        relevant_docs: List[str],
        channel: Channel,
        customer_name: Optional[str],
        sentiment: Sentiment
    ) -> str:
        \"\"\"Generate a response appropriate for the channel\"\"\"
        greeting = self._get_greeting(channel, customer_name)
        body = self._build_response_body(message, relevant_docs)
        closing = self._get_closing(channel)
        escalation_note = self._get_escalation_note(sentiment)

        if channel == Channel.EMAIL:
            return f"{greeting}\\n\\n{body}\\n{escalation_note}\\n\\n{closing}"
        elif channel == Channel.WHATSAPP:
            return f"{greeting} {body[:160]}... {closing}"
        else:
            return f"{greeting}\\n\\n{body}\\n{closing}"

    def _get_greeting(self, channel: Channel, name: Optional[str]) -> str:
        if name:
            name = name.split()[0]
        else:
            name = "there"

        if channel == Channel.EMAIL:
            return f"Dear {name},"
        elif channel == Channel.WHATSAPP:
            return f"Hi {name}!"
        else:
            return f"Hello {name},"

    def _build_response_body(self, message: str, docs: List[str]) -> str:
        \"\"\"Build the main response body from relevant docs\"\"\"
        if not docs:
            return "I couldn't find specific information about your question. Let me escalate this to a human specialist who can help you better."

        response_parts = []
        for doc in docs:
            relevant_part = doc[:200]
            response_parts.append(relevant_part)

        body = "Based on your question, here's what I found:\\n\\n"
        body += "\\n\\n".join(response_parts)
        return body

    def _get_closing(self, channel: Channel) -> str:
        if channel == Channel.EMAIL:
            return "Best regards,\\nTechFlow Support Team"
        elif channel == Channel.WHATSAPP:
            return "Let me know if you need more help! 👍"
        else:
            return "We'll get back to you shortly!"

    def _get_escalation_note(self, sentiment: Sentiment) -> str:
        if sentiment == Sentiment.NEGATIVE:
            return "I understand this is frustrating for you. A human specialist will review your case shortly."
        return ""

    def process_message(
        self,
        message: str,
        channel: Channel,
        customer_id: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> Dict:
        \"\"\"Process a customer message and generate a response\"\"\"
        sentiment = self.analyze_sentiment(message)
        priority = self.determine_priority(message, sentiment)
        relevant_docs = self.search_knowledge_base(message)
        response = self.generate_response(
            message=message,
            relevant_docs=relevant_docs,
            channel=channel,
            customer_name=customer_name,
            sentiment=sentiment
        )
        should_escalate, escalation_reason = self.check_escalation(
            message=message,
            sentiment=sentiment,
            priority=priority,
            category=self.detect_category(message)
        )

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

if __name__ == "__main__":
    agent = CustomerAgent()
    result = agent.process_message(
        message="How do I connect my Slack workspace?",
        channel=Channel.WHATSAPP,
        customer_name="Sarah Chen"
    )
    print(f"Response: {result['response']}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Should Escalate: {result['should_escalate']}")
""")

    # 3. Create submodules structure
    print("Creating agent submodules...")
    for module in ["tools", "prompts", "formatter", "sentiment"]:
        (agent_dir / f"{module}.py").write_text(f"""
# {module.capitalize()} module for Customer Agent
# Placeholder for future implementation
""")

    # 4. Create tests directory
    print("Creating tests/test_agent.py...")
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_agent.py").write_text("""
import pytest
from agent.customer_agent import CustomerAgent, Channel, Sentiment, Priority

@pytest.fixture
def agent():
    return CustomerAgent()

def test_sentiment_positive(agent):
    result = agent.analyze_sentiment("I love this product!")
    assert result == Sentiment.POSITIVE

def test_sentiment_negative(agent):
    result = agent.analyze_sentiment("I'm very frustrated")
    assert result == Sentiment.NEGATIVE

def test_sentiment_neutral(agent):
    result = agent.analyze_sentiment("How does this work?")
    assert result == Sentiment.NEUTRAL

def test_priority_critical(agent):
    result = agent.determine_priority("URGENT system down!", Sentiment.NEUTRAL)
    assert result == Priority.CRITICAL

def test_process_message(agent):
    result = agent.process_message(
        message="How do I use this?",
        channel=Channel.EMAIL,
        customer_name="Test User"
    )
    assert 'response' in result
    assert 'sentiment' in result
    assert 'priority' in result
    assert 'should_escalate' in result
""")

    print("\n✅ Agent scaffold complete!")
    print("\nNext steps:")
    print("  1. Run tests: uv run pytest tests/test_agent.py")
    print("  2. Test agent manually: uv run python src/agent/customer_agent.py")
    print("  3. Use 'fte-mcp-server' skill to create MCP server")


if __name__ == "__main__":
    create_agent_structure()
