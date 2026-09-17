import time
from datetime import datetime, timezone

from .models import LatencyWindow, EventObservation, MarketObservation
from .providers import SofaScoreProvider, OddsApiProvider
from .storage import JsonlStore


class LatencyRadar:
    def __init__(self, interval: float = 2.0) -> None:
        self.interval = interval
        self.events = SofaScoreProvider()
        self.markets = OddsApiProvider()
        self.store = JsonlStore()
        self.seen_events: set[str] = set()
        self.pending_events: dict[str, list[EventObservation]] = {}
        self.last_market_signature: dict[str, str] = {}

    @staticmethod
    def _seconds(a: str, b: str) -> int:
        return int((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() * 1000)

    def _record_market(self, market: MarketObservation) -> None:
        key = f"{market.match_id}:{market.market_id}"
        payload = market.payload or {}
        signature = repr(payload.get("market", payload))
        if self.last_market_signature.get(key) == signature:
            return
        self.last_market_signature[key] = signature
        self.store.append({"type": "market", **market.to_dict()})

        # A market observation after an event is the first measurable reaction.
        pending = self.pending_events.get(market.match_id, [])
        remaining: list[EventObservation] = []
        for event in pending:
            delta = self._seconds(event.observed_at, market.observed_at)
            if 0 <= delta <= 120_000:
                self.store.append({"type": "latency_window", **LatencyWindow(
                    match_id=event.match_id,
                    event_id=event.event_id,
                    event_observed_at=event.observed_at,
                    market_observed_at=market.observed_at,
                    latency_ms=delta,
                    market_status=market.status,
                    source_event=event.source,
                    source_market=market.source,
                ).to_dict()})
            else:
                remaining.append(event)
        self.pending_events[market.match_id] = remaining

    def run_once(self) -> int:
        event_count = 0

        # Capture event feed first, then market feed. This ordering is deliberate:
        # it lets the next market observation become the measured reaction point.
        for match in self.events.live_events():
            for event in self.events.observations(match, self.seen_events):
                self.store.append({"type": "event", **event.to_dict()})
                self.pending_events.setdefault(event.match_id, []).append(event)
                event_count += 1

        if self.markets.api_key:
            for market in self.markets.observations():
                self._record_market(market)

        return event_count

    def run(self) -> None:
        print("SPORTS LATENCY RADAR | PAPER / MEASUREMENT MODE")
        while True:
            started = time.monotonic()
            try:
                count = self.run_once()
                print(f"{datetime.now(timezone.utc).isoformat()} new_events={count}")
            except Exception as exc:
                print(f"collector error: {type(exc).__name__}: {exc}")
            time.sleep(max(0.0, self.interval - (time.monotonic() - started)))
