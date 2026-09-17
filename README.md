# Sports Latency Radar

Detect and measure the time gap between a live sporting event becoming observable and a betting-market update becoming observable.

## Goal

This project is **not** a match-prediction system and **not** a conventional odds-arbitrage scanner. The first phase is measurement:

1. Capture live events from independent sources.
2. Timestamp when each source first reports the event.
3. Record bookmaker/market observations and update timestamps when legally and technically available.
4. Calculate source-to-market latency and stale-market windows.
5. Paper-track hypothetical opportunities only.
6. Build a dataset of recurring latency patterns before considering any further automation.

## Safety / operating mode

The initial system is paper-only. It does not place real bets.

## Initial focus

- Goals
- Red cards
- Penalties
- Second yellow cards
- Substitutions
- Late-match and stoppage-time events
- Source disagreement and timestamp quality
- Market suspension/update timing

## Repository separation

This repository is intentionally separate from the existing sports prediction and Telegram paper-tracking systems.
