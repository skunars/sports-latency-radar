# Sports Latency Radar

This repository measures **event-to-market reaction time** in live sports.

It is deliberately different from a match-prediction bot and from ordinary odds arbitrage.

## Current architecture

`SofaScore live event feed` → `event timestamp` → `market feed` → `market update timestamp` → `latency window` → `append-only dataset`

The football event adapter uses SofaScore event/incident endpoints for live match incidents such as goals and cards.

The market adapter is provider-based. The first adapter supports The Odds API and is intentionally disabled until `ODDS_API_KEY` is supplied. The Odds API exposes live event/odds endpoints and bookmaker-level market data.

## What we measure

- Event observation time
- Market observation time
- Event type
- Market/bookmaker source
- Measured latency in milliseconds
- Repeated latency patterns
- Stale/reaction windows

## Important limitation

A feed timestamp is **not automatically the same thing as a bookmaker's acceptance timestamp**. The first phase therefore measures observable feed-to-market delay. Only after repeated data proves a stable pattern do we investigate execution/acceptance behavior.

## Operating mode

Paper / measurement only. No real bets are placed by this repository.

## Start

```bash
pip install -r requirements.txt
python run_radar.py
```

Set `ODDS_API_KEY` to enable the market adapter. Without it, the event side can still be developed and tested.
