"""Feedback processing and debounce engine for real-time coaching prompts."""

import time

from app.exercises.base import FeedbackEvent, FeedbackSeverity


class FeedbackService:
    """Manages coaching feedback display and suppresses repeated prompt spam."""

    def __init__(self, debounce_seconds: float = 2.5):
        self.debounce_seconds = debounce_seconds
        self.last_emitted: dict[str, float] = {}

    def filter_feedback(self, events: list[FeedbackEvent]) -> list[FeedbackEvent]:
        now = time.time()
        filtered: list[FeedbackEvent] = []

        # Sort so WARNING and GOOD take precedence over INFO
        severity_order = {
            FeedbackSeverity.ERROR: 0,
            FeedbackSeverity.WARNING: 1,
            FeedbackSeverity.GOOD: 2,
            FeedbackSeverity.INFO: 3,
        }
        sorted_events = sorted(events, key=lambda e: severity_order.get(e.severity, 4))

        for ev in sorted_events:
            last_t = self.last_emitted.get(ev.message, 0.0)
            if now - last_t >= self.debounce_seconds:
                filtered.append(ev)
                self.last_emitted[ev.message] = now

        return filtered

    def reset(self):
        self.last_emitted.clear()
