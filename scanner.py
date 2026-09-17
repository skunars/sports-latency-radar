from datetime import datetime

from src.models import EventObservation, MarketObservation
from src.storage import JsonlStore


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def latency_ms(event: EventObservation, market: MarketObservation) -> int:
    delta = parse_iso(market.observed_at) - parse_iso(event.observed_at)
    return max(0, int(delta.total_seconds() * 1000))


def main() -> None:
    store = JsonlStore()
    print(f"sports-latency-radar ready | observations={store.count()}")
    print("Mode: measurement + paper tracking only")


if __name__ == "__main__":
    main()
