"""
Customer Success Agent Prototype
A working prototype that handles customer queries across channels.
"""

from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime
from collections import defaultdict
import re
import json
import os

# Resolve context folder relative to this file so tests work from any CWD
_CONTEXT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "context")

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
        kb_path = os.path.join(_CONTEXT_DIR, "product-docs.md")
        with open(kb_path, 'r') as f:
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

        Args:
            message: Customer's message
            channel: Source channel (email, whatsapp, web_form)
            customer_id: Unique customer identifier
            customer_name: Customer's name for personalization

        Returns:
            Dict containing response, sentiment, and escalation decision
        """
        # Step 1: Analyze sentiment
        sentiment = self.analyze_sentiment(message)

        # Step 2: Determine priority
        priority = self.determine_priority(message, sentiment)

        # Step 3: Search knowledge base
        relevant_docs = self.search_knowledge_base(message)

        # Step 4: Generate response
        response = self.generate_response(
            message=message,
            relevant_docs=relevant_docs,
            channel=channel,
            customer_name=customer_name,
            sentiment=sentiment
        )

        # Step 5: Decide escalation
        should_escalate, escalation_reason = self.check_escalation(
            message=message,
            sentiment=sentiment,
            priority=priority,
            category=self.detect_category(message)
        )

        # Step 6: Store in memory
        if customer_id:
            self.store_conversation(
                customer_id=customer_id,
                message=message,
                response=response,
                channel=channel,
                sentiment=sentiment
            )

        category = self.detect_category(message)
        return {
            "response": response,
            "sentiment": sentiment,
            "should_escalate": should_escalate,
            "escalation_reason": escalation_reason,
            "priority": priority,
            "category": category,
            "channel": channel.value
        }

    def analyze_sentiment(self, message: str) -> Sentiment:
        """Simple sentiment analysis based on keywords"""
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
        """Determine ticket priority based on content and sentiment"""
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
        """
        Simple keyword-based search of product documentation.

        For prototype: Use simple string matching
        For production: Use vector similarity search
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        # Split knowledge base into sections
        sections = self.knowledge_base.split('\n## ')

        scored_sections = []

        for section in sections:
            # Score based on keyword overlap
            section_lower = section.lower()
            section_words = set(re.findall(r'\w+', section_lower))
            overlap = len(query_words & section_words)

            if overlap > 0:
                scored_sections.append((section, overlap))

        # Sort by overlap score and return top 3
        scored_sections.sort(key=lambda x: x[1], reverse=True)
        return [section[0] for section in scored_sections[:3]]

    def generate_response(
        self,
        message: str,
        relevant_docs: List[str],
        channel: Channel,
        customer_name: Optional[str],
        sentiment: Sentiment
    ) -> str:
        """Generate a response appropriate for the channel"""

        greeting = self._get_greeting(channel, customer_name)
        body = self._build_response_body(message, relevant_docs)
        closing = self._get_closing(channel)
        escalation_note = self._get_escalation_note(sentiment)

        if channel == Channel.EMAIL:
            return f"{greeting}\n\n{body}\n{escalation_note}\n\n{closing}"
        elif channel == Channel.WHATSAPP:
            return f"{greeting} {body[:160]}... {closing}"
        else:  # web_form
            return f"{greeting}\n\n{body}\n{closing}"

    def _get_greeting(self, channel: Channel, name: Optional[str]) -> str:
        if name:
            name = name.split()[0]  # First name only
        else:
            name = "there"

        if channel == Channel.EMAIL:
            return f"Dear {name},"
        elif channel == Channel.WHATSAPP:
            return f"Hi {name}!"
        else:  # web_form
            return f"Hello {name},"

    def _build_response_body(self, message: str, docs: List[str]) -> str:
        """Build the main response body from relevant docs"""
        if not docs:
            return "I couldn't find specific information about your question. Let me escalate this to a human specialist who can help you better."

        # Extract relevant information from docs
        response_parts = []
        for doc in docs:
            # Take first 200 chars of each relevant section
            relevant_part = doc[:200]
            response_parts.append(relevant_part)

        body = "Based on your question, here's what I found:\n\n"
        body += "\n\n".join(response_parts)
        return body

    def _get_closing(self, channel: Channel) -> str:
        if channel == Channel.EMAIL:
            return "Best regards,\nTechFlow Support Team"
        elif channel == Channel.WHATSAPP:
            return "Let me know if you need more help! 👍"
        else:  # web_form
            return "We'll get back to you shortly!"

    def _get_escalation_note(self, sentiment: Sentiment) -> str:
        if sentiment == Sentiment.NEGATIVE:
            return "I understand this is frustrating for you. A human specialist will review your case shortly."
        return ""

    def check_escalation(
        self,
        message: str,
        sentiment: Sentiment,
        priority: Priority,
        category: str
    ) -> tuple[bool, str]:
        """
        Check if this should be escalated to human support.

        Returns:
            (should_escalate: bool, reason: str)
        """
        # Load escalation rules
        rules_path = os.path.join(_CONTEXT_DIR, "escalation-rules.md")
        with open(rules_path, 'r') as f:
            escalation_rules = f.read()

        # Check negative sentiment
        if sentiment == Sentiment.NEGATIVE:
            return True, "Negative customer sentiment detected"

        # Check for billing issues
        billing_keywords = ['refund', 'payment', 'pricing', 'discount', 'negotiate']
        if any(kw in message.lower() for kw in billing_keywords):
            return True, "Billing/pricing related inquiry"

        # Check for compliance/legal
        compliance_keywords = ['hipaa', 'gdpr', 'soc2', 'legal', 'compliance', 'baa']
        if any(kw in message.lower() for kw in compliance_keywords):
            return True, "Compliance/legal inquiry"

        # Check critical priority
        if priority == Priority.CRITICAL:
            return True, "Critical priority issue"

        # Check for feature requests
        if category == "feature_request":
            return True, "Feature request - needs product team review"

        return False, ""

    def detect_category(self, message: str) -> str:
        """Detect the category of the customer's inquiry"""
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
        """Store conversation in memory (prototype uses in-memory dict)"""
        if customer_id not in self.conversation_memory:
            self.conversation_memory[customer_id] = []

        self.conversation_memory[customer_id].append({
            "message": message,
            "response": response,
            "channel": channel,
            "sentiment": sentiment,
            "timestamp": str(datetime.now())
        })

    def get_customer_history(self, customer_id: str) -> List[Dict]:
        """Get conversation history for a customer"""
        return self.conversation_memory.get(customer_id, [])

# Example usage
if __name__ == "__main__":
    from datetime import datetime

    agent = CustomerAgent()

    # Test with different channels
    test_messages = [
        {
            "message": "How do I connect my Slack workspace?",
            "channel": Channel.WHATSAPP,
            "customer_name": "Sarah Chen"
        },
        {
            "message": "My workflow isn't executing and I've been trying for hours!",
            "channel": Channel.EMAIL,
            "customer_name": "John Doe"
        },
        {
            "message": "Can you add support for Asana integration?",
            "channel": Channel.WEB_FORM,
            "customer_name": "Mike Johnson"
        }
    ]

    for test in test_messages:
        result = agent.process_message(
            message=test["message"],
            channel=test["channel"],
            customer_name=test["customer_name"]
        )

        print(f"\n{'='*50}")
        print(f"Channel: {test['channel'].value}")
        print(f"Customer: {test['customer_name']}")
        print(f"Message: {test['message']}")
        print(f"\nResponse:\n{result['response']}")
        print(f"\nSentiment: {result['sentiment']}")
        print(f"Priority: {result['priority']}")
        print(f"Escalate: {result['should_escalate']}")
        if result['should_escalate']:
            print(f"Reason: {result['escalation_reason']}")
