from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EventObservation:
    match_id: str
    event_id: str
    event_type: str
    source: str
    observed_at: str
    event_clock: Optional[str] = None
    payload: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MarketObservation:
    match_id: str
    market_id: str
    source: str
    observed_at: str
    status: str
    price: Optional[float] = None
    payload: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LatencyWindow:
    match_id: str
    event_id: str
    event_observed_at: str
    market_observed_at: str
    latency_ms: int
    market_status: str
    source_event: str
    source_market: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
