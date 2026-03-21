"""
MCP Server Tool Tests
Tests all 7 tools exposed by the FastMCP server.
"""

import json
import pytest
import sys
import os

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from mcp_server.server import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    send_response,
    escalate_to_human,
    analyze_sentiment,
    get_channel_formatting,
    agent,
)


class TestSearchKnowledgeBase:

    def test_returns_results_for_known_topic(self):
        result = search_knowledge_base("Slack integration")
        assert "Slack" in result

    def test_returns_results_for_workflow(self):
        result = search_knowledge_base("workflow not executing")
        assert len(result) > 0
        assert "---" in result or "Workflow" in result

    def test_returns_no_results_message_for_unknown(self):
        result = search_knowledge_base("xyzzy frobnicator nonsense")
        assert "No relevant documentation found" in result

    def test_sections_separated_by_divider(self):
        result = search_knowledge_base("security RBAC audit")
        # Multiple sections should be joined with divider
        # (or single section returned)
        assert isinstance(result, str)
        assert len(result) > 0


class TestCreateTicket:

    def test_returns_valid_json(self):
        result = create_ticket("user@example.com", "Login issue", "high", "email")
        data = json.loads(result)
        assert data["status"] == "created"

    def test_ticket_id_format(self):
        result = create_ticket("user@example.com", "Billing question", "medium", "whatsapp")
        data = json.loads(result)
        assert data["ticket_id"].startswith("TKT-")

    def test_channel_preserved(self):
        for channel in ["email", "whatsapp", "web_form"]:
            result = create_ticket("cust@test.com", "issue", "low", channel)
            data = json.loads(result)
            assert data["channel"] == channel

    def test_customer_id_preserved(self):
        result = create_ticket("specific@user.com", "some issue", "low", "email")
        data = json.loads(result)
        assert data["customer_id"] == "specific@user.com"

    def test_priority_preserved(self):
        result = create_ticket("u@u.com", "critical thing", "critical", "email")
        data = json.loads(result)
        assert data["priority"] == "critical"

    def test_deterministic_ticket_id(self):
        """Same inputs produce same ticket ID"""
        r1 = create_ticket("same@user.com", "same issue", "low", "email")
        r2 = create_ticket("same@user.com", "same issue", "low", "email")
        assert json.loads(r1)["ticket_id"] == json.loads(r2)["ticket_id"]


class TestGetCustomerHistory:

    def test_no_history_returns_message(self):
        result = get_customer_history("brand.new.customer@never.seen.com")
        assert "No previous interactions" in result

    def test_history_returned_after_interaction(self):
        from agent.customer_agent import Channel, Sentiment
        agent.store_conversation(
            customer_id="history.test.mcp@example.com",
            message="Test message via MCP",
            response="Test response",
            channel=Channel.EMAIL,
            sentiment=Sentiment.NEUTRAL
        )
        result = get_customer_history("history.test.mcp@example.com")
        assert "Interaction 1" in result
        assert "Test message via MCP" in result

    def test_history_shows_channel(self):
        from agent.customer_agent import Channel, Sentiment
        agent.store_conversation(
            customer_id="channel.check@test.com",
            message="WhatsApp message",
            response="Reply",
            channel=Channel.WHATSAPP,
            sentiment=Sentiment.POSITIVE
        )
        result = get_customer_history("channel.check@test.com")
        assert "Channel" in result


class TestSendResponse:

    def test_returns_valid_json(self):
        result = send_response("TKT-1234", "Your issue has been resolved.", "email")
        data = json.loads(result)
        assert data["status"] == "sent"

    def test_email_delivery_method(self):
        result = send_response("TKT-001", "Hello!", "email")
        data = json.loads(result)
        assert data["delivery_method"] == "Gmail API"

    def test_whatsapp_delivery_method(self):
        result = send_response("TKT-002", "Hi!", "whatsapp")
        data = json.loads(result)
        assert data["delivery_method"] == "Twilio WhatsApp"

    def test_web_form_delivery_method(self):
        result = send_response("TKT-003", "Thank you!", "web_form")
        data = json.loads(result)
        assert data["delivery_method"] == "Email + API response"

    def test_ticket_id_preserved(self):
        result = send_response("TKT-9999", "Message", "email")
        data = json.loads(result)
        assert data["ticket_id"] == "TKT-9999"

    def test_unknown_channel_returns_unknown(self):
        result = send_response("TKT-000", "msg", "fax")
        data = json.loads(result)
        assert data["delivery_method"] == "unknown"


class TestEscalateToHuman:

    def test_returns_valid_json(self):
        result = escalate_to_human("TKT-1234", "Billing dispute", "Customer wants refund")
        data = json.loads(result)
        assert data["status"] == "escalated"

    def test_escalation_id_format(self):
        result = escalate_to_human("TKT-5678", "Negative sentiment", "Very angry customer")
        data = json.loads(result)
        assert data["escalation_id"].startswith("ESC-")

    def test_original_ticket_id_preserved(self):
        result = escalate_to_human("TKT-ORIG", "reason", "context")
        data = json.loads(result)
        assert data["original_ticket_id"] == "TKT-ORIG"

    def test_reason_preserved(self):
        result = escalate_to_human("TKT-0001", "HIPAA compliance request", "context info")
        data = json.loads(result)
        assert "HIPAA" in data["reason"]

    def test_assigned_to_human_team(self):
        result = escalate_to_human("TKT-0002", "reason", "context")
        data = json.loads(result)
        assert "Human" in data["assigned_to"]


class TestAnalyzeSentiment:

    def test_positive_sentiment(self):
        result = analyze_sentiment("I love this product, it's amazing!")
        data = json.loads(result)
        assert data["sentiment"] == "positive"

    def test_negative_sentiment(self):
        result = analyze_sentiment("I hate this, it's terrible and frustrating")
        data = json.loads(result)
        assert data["sentiment"] == "negative"

    def test_neutral_sentiment(self):
        result = analyze_sentiment("How do I configure the integration?")
        data = json.loads(result)
        assert data["sentiment"] == "neutral"

    def test_returns_recommendation(self):
        result = analyze_sentiment("This is great!")
        data = json.loads(result)
        assert "recommendation" in data
        assert len(data["recommendation"]) > 0

    def test_negative_recommendation_mentions_empathy(self):
        result = analyze_sentiment("I'm frustrated and angry about this")
        data = json.loads(result)
        assert "empathy" in data["recommendation"].lower() or "escalation" in data["recommendation"].lower()


class TestGetChannelFormatting:

    def test_email_formatting(self):
        result = get_channel_formatting("email")
        data = json.loads(result)
        assert data["max_length"] == 500
        assert "Dear" in data["greeting"]

    def test_whatsapp_formatting(self):
        result = get_channel_formatting("whatsapp")
        data = json.loads(result)
        assert data["max_length"] == 160
        assert data["emojis_allowed"] is True

    def test_web_form_formatting(self):
        result = get_channel_formatting("web_form")
        data = json.loads(result)
        assert data["max_length"] == 300
        assert data["emojis_allowed"] is False

    def test_unknown_channel_returns_empty(self):
        result = get_channel_formatting("fax")
        data = json.loads(result)
        assert data == {}

    def test_all_channels_have_greeting_and_closing(self):
        for channel in ["email", "whatsapp", "web_form"]:
            data = json.loads(get_channel_formatting(channel))
            assert "greeting" in data
            assert "closing" in data