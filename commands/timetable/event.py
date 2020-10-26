# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from __future__ import annotations

from typing import List
from datetime import datetime as DateTime, timedelta as TimeDelta

# Event class
class Event():
    def __init__(
        self,
        title: str,
        location: str,
        starts: DateTime,
        ends: DateTime,
        invitees: List[str],
        events: List[Event] = None,
        rrule: TimeDelta = None
    ):
        self.title: str = title
        self.location: str = location
        self.starts: DateTime = starts
        self.ends: DateTime = ends
        self.invitees: List[str] = invitees
        self.events: List[Event] = events or []
        self._rrule = rrule

    # Determine if event is equal to another event
    def __eq__(self, event: Event) -> bool:
        if self.title != event.title:
            return False

        if self.location != event.location:
            return False

        if self.invitees != event.invitees:
            return False

        return True

    # Hash the event
    def __hash__(self) -> int:
        return hash((self.starts, self.ends))

    # Compute the recurrence rule, removing subevents that satisfy it
    @property
    def rrule(self):
        if self._rrule:
            return self._rrule

        diffs: List[TimeDelta] = []

        for i, event in enumerate(self.events):
            try:
                next: Event = self.events[i + 1]
            except IndexError:
                continue

            diffs.append(next.starts - event.starts)
            diffs.append(next.ends - event.ends)