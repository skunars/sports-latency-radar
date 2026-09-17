import os
from datetime import datetime, timezone
from typing import Any

import requests

from .models import EventObservation, MarketObservation, utc_now


class SofaScoreProvider:
    BASE = "https://www.sofascore.com/api/v1"

    def __init__(self, timeout: float = 8.0) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 sports-latency-radar/1.0"})

    def live_events(self) -> list[dict[str, Any]]:
        r = self.session.get(f"{self.BASE}/sport/football/scheduled-events/{datetime.now(timezone.utc):%Y-%m-%d}", timeout=self.timeout)
        r.raise_for_status()
        return [e for e in r.json().get("events", []) if e.get("status", {}).get("type") == "inprogress"]

    def incidents(self, event_id: int) -> list[dict[str, Any]]:
        r = self.session.get(f"{self.BASE}/event/{event_id}/incidents", timeout=self.timeout)
        r.raise_for_status()
        return r.json().get("incidents", [])

    def observations(self, event: dict[str, Any], seen: set[str]) -> list[EventObservation]:
        event_id = str(event["id"])
        home = event.get("homeTeam", {}).get("name", "home")
        away = event.get("awayTeam", {}).get("name", "away")
        out: list[EventObservation] = []
        for incident in self.incidents(int(event_id)):
            kind = incident.get("incidentType")
            if kind not in {"goal", "card", "substitution", "incident"}:
                continue
            key = f"{event_id}:{incident.get('id', hash(str(incident)))}"
            if key in seen:
                continue
            seen.add(key)
            out.append(EventObservation(
                match_id=event_id,
                event_id=key,
                event_type=str(kind),
                source="sofascore",
                observed_at=utc_now(),
                event_clock=str(incident.get("time", "")),
                payload={"home": home, "away": away, "incident": incident},
            ))
        return out


class OddsApiProvider:
    BASE = "https://api.the-odds-api.com/v4"

    def __init__(self, api_key: str | None = None, timeout: float = 8.0) -> None:
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        self.timeout = timeout
        self.session = requests.Session()

    def observations(self, sport: str = "soccer_epl", regions: str = "eu", markets: str = "h2h") -> list[MarketObservation]:
        if not self.api_key:
            return []
        r = self.session.get(
            f"{self.BASE}/sports/{sport}/odds",
            params={"apiKey": self.api_key, "regions": regions, "markets": markets, "oddsFormat": "decimal"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        now = utc_now()
        out: list[MarketObservation] = []
        for event in r.json():
            for book in event.get("bookmakers", []):
                for market in book.get("markets", []):
                    out.append(MarketObservation(
                        match_id=str(event.get("id")),
                        market_id=f"{book.get('key')}:{market.get('key')}",
                        source=str(book.get("key", "odds-api")),
                        observed_at=now,
                        status="open",
                        payload={"event": event, "market": market},
                    ))
        return out
