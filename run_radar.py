import os

from src.radar import LatencyRadar


if __name__ == "__main__":
    interval = float(os.getenv("POLL_INTERVAL_SECONDS", "2"))
    LatencyRadar(interval=interval).run()
