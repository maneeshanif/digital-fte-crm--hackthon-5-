"""
Customer Success Agent Template
Copy this template and customize for your specific FTE implementation
"""

from typing import Dict, Optional, List
from enum import Enum
from datetime import datetime
from collections import defaultdict
import re


# CUSTOMIZE: Adjust these enums based on your needs
class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"
    # Add more channels as needed


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# CUSTOMIZE: Main agent class
class CustomerAgent:
    """Prototype Customer Success Agent"""

    def __init__(self):
        self.load_knowledge_base()
        self.conversation_memory = defaultdict(list)
        self.customer_sentiment_history = defaultdict(list)

    def load_knowledge_base(self):
        """CUSTOMIZE: Load your knowledge base from appropriate location"""
        # Example: Load from context/product-docs.md
        try:
            with open('context/product-docs.md', 'r') as f:
                self.knowledge_base = f.read()
        except FileNotFoundError:
            print("Warning: Knowledge base file not found")
            self.knowledge_base = ""

    # CUSTOMIZE: Add or modify methods below based on your requirements

    def analyze_sentiment(self, message: str) -> Sentiment:
        """
        CUSTOMIZE: Implement your sentiment analysis logic
        This is a simple keyword-based implementation
        """
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
        """
        CUSTOMIZE: Implement your priority determination logic
        """
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
        CUSTOMIZE: Implement your knowledge base search
        Consider upgrading to vector similarity search for production
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        sections = self.knowledge_base.split('\n## ')
        scored_sections = []

        for section in sections:
            section_lower = section.lower()
            section_words = set(re.findall(r'\w+', section_lower))
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
        """
        CUSTOMIZE: Implement your escalation rules
        Load from context/escalation-rules.md
        """
        try:
            with open('context/escalation-rules.md', 'r') as f:
                escalation_rules = f.read()
        except FileNotFoundError:
            print("Warning: Escalation rules file not found")

        # CUSTOMIZE: Adjust escalation logic based on your rules
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
        """
        CUSTOMIZE: Implement your category detection
        Adjust keywords based on your product
        """
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
        """Store conversation in memory"""
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

    def generate_response(
        self,
        message: str,
        relevant_docs: List[str],
        channel: Channel,
        customer_name: Optional[str],
        sentiment: Sentiment
    ) -> str:
        """
        CUSTOMIZE: Implement your response generation logic
        Consider using LLM for production
        """
        greeting = self._get_greeting(channel, customer_name)
        body = self._build_response_body(message, relevant_docs)
        closing = self._get_closing(channel)
        escalation_note = self._get_escalation_note(sentiment)

        if channel == Channel.EMAIL:
            return f"{greeting}\n\n{body}\n{escalation_note}\n\n{closing}"
        elif channel == Channel.WHATSAPP:
            return f"{greeting} {body[:160]}... {closing}"
        else:
            return f"{greeting}\n\n{body}\n{closing}"

    def _get_greeting(self, channel: Channel, name: Optional[str]) -> str:
        """CUSTOMIZE: Adjust greetings based on brand voice"""
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
        """CUSTOMIZE: Adjust response body construction"""
        if not docs:
            return "I couldn't find specific information about your question. Let me escalate this to a human specialist who can help you better."

        response_parts = []
        for doc in docs:
            relevant_part = doc[:200]
            response_parts.append(relevant_part)

        body = "Based on your question, here's what I found:\n\n"
        body += "\n\n".join(response_parts)
        return body

    def _get_closing(self, channel: Channel) -> str:
        """CUSTOMIZE: Adjust closings based on brand voice"""
        if channel == Channel.EMAIL:
            return "Best regards,\n[COMPANY_NAME] Support Team"
        elif channel == Channel.WHATSAPP:
            return "Let me know if you need more help! 👍"
        else:
            return "We'll get back to you shortly!"

    def _get_escalation_note(self, sentiment: Sentiment) -> str:
        """CUSTOMIZE: Adjust escalation note based on brand voice"""
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
        """
        Main entry point for processing customer messages
        CUSTOMIZE: Add or modify steps as needed
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

        # Step 5: Check escalation
        should_escalate, escalation_reason = self.check_escalation(
            message=message,
            sentiment=sentiment,
            priority=priority,
            category=self.detect_category(message)
        )

        # Step 6: Store conversation
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


# CUSTOMIZE: Example usage
if __name__ == "__main__":
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
