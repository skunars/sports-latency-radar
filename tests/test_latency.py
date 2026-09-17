from src.models import EventObservation, MarketObservation
from scanner import latency_ms


def test_latency_ms():
    event = EventObservation(
        match_id="m1", event_id="e1", event_type="goal", source="feed-a",
        observed_at="2026-09-17T20:00:00.000000+00:00",
    )
    market = MarketObservation(
        match_id="m1", market_id="x", source="book-a",
        observed_at="2026-09-17T20:00:03.250000+00:00", status="open",
    )
    assert latency_ms(event, market) == 3250
