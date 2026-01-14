"""
Epistemic Metrics - Computed metrics for client relationships

Computes aggregate epistemic state from interaction history, memory, and engagements:
- relationship_health: Quality of the relationship (0-1)
- knowledge_depth: How well we understand the client (0-1)
- engagement_frequency: Interactions per week
"""

import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def compute_relationship_health(
    client_id: str,
    days: int = 30,
) -> Dict[str, Any]:
    """
    Compute relationship health score based on:
    - Interaction frequency and recency
    - Sentiment distribution (positive > negative)
    - Engagement outcomes (won vs lost)
    - Follow-up responsiveness

    Returns dict with score (0-1) and breakdown.
    """
    from .interaction_store import InteractionStore
    from .engagement_store import EngagementStore

    interaction_store = InteractionStore()
    engagement_store = EngagementStore()

    try:
        # Get activity stats
        stats = interaction_store.get_client_activity_stats(client_id, days)
        total_interactions = stats.get("total_interactions", 0)
        sentiment = stats.get("by_sentiment", {})
        frequency = stats.get("engagement_frequency", 0)

        # Get pending follow-ups (lower is better)
        pending = interaction_store.get_pending_follow_ups(client_id)
        pending_count = len(pending)

        # Get engagement outcomes
        engagements = engagement_store.list(client_id=client_id, status="completed", limit=10)
        won = sum(1 for e in engagements if e.outcome == "won")
        lost = sum(1 for e in engagements if e.outcome == "lost")
        total_completed = len(engagements)

        # Compute component scores
        # Frequency score: 2+ interactions/week is ideal
        frequency_score = min(1.0, frequency / 2.0)

        # Sentiment score: ratio of positive to total sentiment-tagged interactions
        positive = sentiment.get("positive", 0)
        negative = sentiment.get("negative", 0)
        neutral = sentiment.get("neutral", 0)
        sentiment_total = positive + negative + neutral
        if sentiment_total > 0:
            sentiment_score = (positive + 0.5 * neutral) / sentiment_total
        else:
            sentiment_score = 0.5  # neutral default

        # Outcome score: win rate
        if total_completed > 0:
            outcome_score = won / total_completed
        else:
            outcome_score = 0.5  # no data

        # Responsiveness score: penalize pending follow-ups
        responsiveness_score = max(0, 1.0 - (pending_count * 0.2))

        # Recency score: bonus for recent contact
        recency_score = 0.5
        if total_interactions > 0:
            # Get most recent interaction
            recent = interaction_store.list(client_id=client_id, limit=1)
            if recent:
                days_since = (time.time() - recent[0].occurred_at) / 86400
                recency_score = max(0, 1.0 - (days_since / 14))  # 2 weeks decay

        # Weighted composite
        weights = {
            "frequency": 0.2,
            "sentiment": 0.25,
            "outcome": 0.25,
            "responsiveness": 0.15,
            "recency": 0.15,
        }

        health_score = (
            frequency_score * weights["frequency"] +
            sentiment_score * weights["sentiment"] +
            outcome_score * weights["outcome"] +
            responsiveness_score * weights["responsiveness"] +
            recency_score * weights["recency"]
        )

        return {
            "relationship_health": round(health_score, 3),
            "breakdown": {
                "frequency_score": round(frequency_score, 3),
                "sentiment_score": round(sentiment_score, 3),
                "outcome_score": round(outcome_score, 3),
                "responsiveness_score": round(responsiveness_score, 3),
                "recency_score": round(recency_score, 3),
            },
            "raw_data": {
                "total_interactions": total_interactions,
                "interactions_per_week": round(frequency, 2),
                "sentiment_distribution": sentiment,
                "pending_follow_ups": pending_count,
                "engagements_won": won,
                "engagements_lost": lost,
            },
            "period_days": days,
        }
    finally:
        interaction_store.close()
        engagement_store.close()


def compute_knowledge_depth(
    client_id: str,
) -> Dict[str, Any]:
    """
    Compute knowledge depth score based on:
    - Number of findings (what we know)
    - Average confidence of findings
    - Coverage of key topics
    - Resolved vs unresolved unknowns

    Returns dict with score (0-1) and breakdown.
    """
    from .client_memory import get_client_context

    context = get_client_context(client_id, limit=100)

    findings = context.get("findings", [])
    unknowns = context.get("unknowns", [])
    patterns = context.get("patterns", [])

    # Count findings
    finding_count = len(findings)
    pattern_count = len(patterns)
    unknown_count = len(unknowns)

    # Average confidence of findings
    if findings:
        avg_confidence = sum(f.get("confidence", 0.5) for f in findings) / len(findings)
    else:
        avg_confidence = 0.0

    # Average impact of findings
    if findings:
        avg_impact = sum(f.get("impact", 0.5) for f in findings) / len(findings)
    else:
        avg_impact = 0.0

    # Compute component scores

    # Volume score: More findings = deeper knowledge (diminishing returns)
    # 10 findings = 0.5, 20 = 0.7, 50+ = 0.9
    volume_score = min(0.95, (finding_count + pattern_count) / 50)

    # Confidence score: Higher confidence = more certain knowledge
    confidence_score = avg_confidence

    # Resolution score: Fewer unknowns relative to findings is better
    total_items = finding_count + unknown_count + pattern_count
    if total_items > 0:
        resolution_score = (finding_count + pattern_count) / total_items
    else:
        resolution_score = 0.0

    # Impact score: High-impact findings = valuable knowledge
    impact_score = avg_impact

    # Weighted composite
    weights = {
        "volume": 0.25,
        "confidence": 0.30,
        "resolution": 0.20,
        "impact": 0.25,
    }

    depth_score = (
        volume_score * weights["volume"] +
        confidence_score * weights["confidence"] +
        resolution_score * weights["resolution"] +
        impact_score * weights["impact"]
    )

    return {
        "knowledge_depth": round(depth_score, 3),
        "breakdown": {
            "volume_score": round(volume_score, 3),
            "confidence_score": round(confidence_score, 3),
            "resolution_score": round(resolution_score, 3),
            "impact_score": round(impact_score, 3),
        },
        "raw_data": {
            "finding_count": finding_count,
            "pattern_count": pattern_count,
            "unknown_count": unknown_count,
            "avg_confidence": round(avg_confidence, 3),
            "avg_impact": round(avg_impact, 3),
        },
    }


def compute_all_metrics(
    client_id: str,
    days: int = 30,
    update_client: bool = False,
) -> Dict[str, Any]:
    """
    Compute all epistemic metrics for a client.

    Args:
        client_id: Client UUID
        days: Period for relationship health calculation
        update_client: If True, update the client record with computed values

    Returns:
        Dict with relationship_health, knowledge_depth, and breakdowns
    """
    health = compute_relationship_health(client_id, days)
    depth = compute_knowledge_depth(client_id)

    result = {
        "client_id": client_id,
        "relationship_health": health["relationship_health"],
        "knowledge_depth": depth["knowledge_depth"],
        "health_breakdown": health["breakdown"],
        "depth_breakdown": depth["breakdown"],
        "health_raw_data": health["raw_data"],
        "depth_raw_data": depth["raw_data"],
        "computed_at": time.time(),
    }

    if update_client:
        from .client_store import update_client as do_update
        do_update(
            client_id,
            relationship_health=health["relationship_health"],
            knowledge_depth=depth["knowledge_depth"],
        )
        result["client_updated"] = True

    return result


def get_client_epistemic_state(client_id: str) -> Dict[str, Any]:
    """
    Get comprehensive epistemic state for a client.

    Combines:
    - Current computed metrics
    - Client memory context
    - Pending actions

    Useful for AI grounding before client interactions.
    """
    from .client_store import get_client
    from .client_memory import get_client_context
    from .interaction_store import get_pending_follow_ups

    client = get_client(client_id)
    if client is None:
        return {"error": f"Client {client_id} not found"}

    # Compute fresh metrics
    metrics = compute_all_metrics(client_id)

    # Get memory context
    context = get_client_context(client_id, limit=10)

    # Get pending follow-ups
    follow_ups = get_pending_follow_ups(client_id)

    return {
        "client": {
            "client_id": client.client_id,
            "name": client.name,
            "client_type": client.client_type,
            "status": client.status,
            "last_contact_at": client.last_contact_at,
        },
        "metrics": {
            "relationship_health": metrics["relationship_health"],
            "knowledge_depth": metrics["knowledge_depth"],
        },
        "memory": {
            "top_findings": context.get("findings", [])[:5],
            "open_unknowns": context.get("unknowns", [])[:5],
            "patterns": context.get("patterns", [])[:3],
        },
        "actions": {
            "next_action": client.next_action,
            "next_action_due": client.next_action_due,
            "pending_follow_ups": [
                {"id": f.interaction_id, "notes": f.follow_up_notes}
                for f in follow_ups[:5]
            ],
        },
        "computed_at": time.time(),
    }
