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
        self.last_market: dict[str, MarketObservation] = {}

    def run_once(self) -> int:
        event_count = 0
        for match in self.events.live_events():
            for event in self.events.observations(match, self.seen_events):
                self.store.append({"type": "event", **event.to_dict()})
                event_count += 1
                market = self.last_market.get(event.match_id)
                if market:
                    latency = max(0, int((datetime.fromisoformat(market.observed_at) - datetime.fromisoformat(event.observed_at)).total_seconds() * 1000))
                    self.store.append({"type": "latency_window", **LatencyWindow(
                        match_id=event.match_id,
                        event_id=event.event_id,
                        event_observed_at=event.observed_at,
                        market_observed_at=market.observed_at,
                        latency_ms=latency,
                        market_status=market.status,
                        source_event=event.source,
                        source_market=market.source,
                    ).to_dict()})

        if self.markets.api_key:
            for market in self.markets.observations():
                key = f"{market.match_id}:{market.market_id}"
                self.last_market[key] = market
                self.last_market[market.match_id] = market
                self.store.append({"type": "market", **market.to_dict()})
        return event_count

    def run(self) -> None:
        print("SPORTS LATENCY RADAR | PAPER / MEASUREMENT MODE")
        while True:
            started = time.monotonic()
            try:
                count = self.run_once()
                print(f"{datetime.now(timezone.utc).isoformat()} events={count}")
            except Exception as exc:
                print(f"collector error: {type(exc).__name__}: {exc}")
            time.sleep(max(0.0, self.interval - (time.monotonic() - started)))
