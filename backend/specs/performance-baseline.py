"""
Performance Baseline Measurement Script
Run from backend/ directory: uv run python specs/performance-baseline.py
"""

import json
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent.customer_agent import CustomerAgent, Channel

def load_tickets():
    tickets_path = os.path.join(os.path.dirname(__file__), "..", "context", "sample-tickets.json")
    with open(tickets_path) as f:
        return json.load(f)["tickets"]

CHANNEL_MAP = {
    "email": Channel.EMAIL,
    "whatsapp": Channel.WHATSAPP,
    "web_form": Channel.WEB_FORM,
}

def run_baseline():
    agent = CustomerAgent()
    tickets = load_tickets()

    results = []
    response_times = []

    sentiment_correct = 0
    escalation_triggered = 0
    category_counts = {}

    print(f"Running baseline on {len(tickets)} tickets...\n")

    for ticket in tickets:
        channel = CHANNEL_MAP.get(ticket["channel"], Channel.EMAIL)
        customer = ticket["customer"]
        customer_id = customer.get("email") or customer.get("phone", "unknown")
        customer_name = customer.get("name", "Customer")
        message = ticket["message"]

        start = time.perf_counter()
        result = agent.process_message(
            message=message,
            channel=channel,
            customer_id=customer_id,
            customer_name=customer_name
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        response_times.append(elapsed_ms)

        # Sentiment accuracy (compare predicted vs ground truth)
        predicted_sentiment = result["sentiment"].value if hasattr(result["sentiment"], "value") else str(result["sentiment"])
        expected_sentiment = ticket.get("sentiment", "neutral")
        if predicted_sentiment == expected_sentiment:
            sentiment_correct += 1

        if result["should_escalate"]:
            escalation_triggered += 1

        cat = result["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

        results.append({
            "id": ticket["id"],
            "channel": ticket["channel"],
            "response_time_ms": round(elapsed_ms, 3),
            "sentiment_match": predicted_sentiment == expected_sentiment,
            "predicted_sentiment": predicted_sentiment,
            "expected_sentiment": expected_sentiment,
            "escalated": result["should_escalate"],
            "category": cat,
        })

    total = len(tickets)
    avg_ms = sum(response_times) / total
    max_ms = max(response_times)
    min_ms = min(response_times)

    sentiment_accuracy = (sentiment_correct / total) * 100
    escalation_rate = (escalation_triggered / total) * 100

    print("=" * 55)
    print("PERFORMANCE BASELINE RESULTS")
    print("=" * 55)
    print(f"\nTickets processed   : {total}")
    print(f"\n-- Response Time --")
    print(f"  Average           : {avg_ms:.3f} ms")
    print(f"  Min               : {min_ms:.3f} ms")
    print(f"  Max               : {max_ms:.3f} ms")
    print(f"\n-- Accuracy --")
    print(f"  Sentiment accuracy: {sentiment_accuracy:.1f}% ({sentiment_correct}/{total})")
    print(f"  Escalation rate   : {escalation_rate:.1f}% ({escalation_triggered}/{total})")
    print(f"\n-- Category Distribution --")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat:<20}: {count}")

    print(f"\n-- Per-Channel Breakdown --")
    for ch in ["email", "whatsapp", "web_form"]:
        ch_results = [r for r in results if r["channel"] == ch]
        if ch_results:
            ch_avg = sum(r["response_time_ms"] for r in ch_results) / len(ch_results)
            ch_sentiment_ok = sum(1 for r in ch_results if r["sentiment_match"])
            print(f"  {ch:<12}: {len(ch_results)} tickets | avg {ch_avg:.3f}ms | sentiment {ch_sentiment_ok}/{len(ch_results)}")

    print("\n-- Mismatched Sentiments --")
    mismatches = [r for r in results if not r["sentiment_match"]]
    if mismatches:
        for m in mismatches:
            print(f"  Ticket #{m['id']}: expected={m['expected_sentiment']} got={m['predicted_sentiment']}")
    else:
        print("  None")

    print("\n" + "=" * 55)

if __name__ == "__main__":
    run_baseline()