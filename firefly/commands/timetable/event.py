# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from __future__ import annotations

import sys
from itertools import product
from collections import Counter
from typing import List, Dict, Tuple
from datetime import datetime as DateTime, timedelta as TimeDelta

# Rule to generate occurences
class RecurrenceRule():
    # Create an instance
    def __init__(self, interval: TimeDelta, count: int = None, until: DateTime = None):
        if count and until or not count and not until:
            raise ValueError('Please specify count or until (but not both) as per RFC 5545. See https://icalendar.org/iCalendar-RFC-5545/3-3-10-recurrence-rule.html.')

        self.interval: TimeDelta = interval
        self.count: int = count
        self.until: DateTime = until

# Event class
class Event():
    # Attributes that default to the parent's value
    INHERITABLE: List[str] = ['title', 'location']

    # Create an instance
    def __init__(
        self,
        start: DateTime,
        end: DateTime,
        title: str = None,
        location: str = None,
        parent: Event = None,
        rrule: RecurrenceRule = None,
        occurences: EventSet = None,
        exrule: RecurrenceRule = None,
        exceptions: EventSet = None
    ):
        self.start: DateTime = start
        self.end: DateTime = end
        self.title: str = title
        self.location: str = location
        self.parent: Event = parent
        self._rrule: RecurrenceRule = rrule
        self._additions: EventSet = occurences
        self._exrule: RecurrenceRule = exrule
        self._exceptions: EventSet = exceptions

    # Compute the duration
    @property
    def duration(self) -> TimeDelta:
        return self.end - self.start

    # Compute the recurrence rule
    @property
    def rrule(self) -> RecurrenceRule:
        return self._rrule

    # Set the recurrence rule
    @rrule.setter
    def rrule(self, value: TimeDelta):
        self._rrule = value

    # Compute all the occurences
    @property
    def occurences(self) -> EventSet:
        return [self] + self.repeats + self._additions

    # Compute all the repeats
    @property
    def repeats(self, rrule: RecurrenceRule = None):
        repeats: EventSet = EventSet()
        rrule = rrule or self._rrule
        event: Event = self

        while True:
            if rrule.count and len(repeats) >= rrule.count:
                break

            if rrule.until and repeats[-1].end >= rrule.until:
                break

            event = Event(
                start=event.start + rrule.interval,
                end=event.end + rrule.interval,
                parent=self
            )

            repeats.append(event)

        return repeats

    # Determine if another Event is equal
    def __eq__(self, other: Event) -> bool:
        for attr in self.INHERITABLE:
            if getattr(other, attr) != getattr(self, attr):
                return False

        return True

    # Get an attribute if it isn't set
    def __getattr__(self, attr: str):
        if self.parent and attr in self.INHERITABLE:
            # Delegate to the parent event
            return getattr(self.parent, attr)

        return None

# Set of events
class EventSet(List[Event]):
    # Create an instance
    def __init__(self, *args, **kwargs):
        self._freq: int = 1
        self._delta: TimeDelta = None
        super().__init__(*args, **kwargs)
        self.group()

    # Compute the duration
    @property
    def duration(self):
        return self[-1].end - self[0].start

    # Group into equal and repeating events
    def group(self):
        # List of recurring subsets
        subsets: List[EventSet]

        for start in range(len(self)):
            for end in range(start, len(self[start:])):
                sys.exit(str(start) + ' ' + str(end))
                subset: EventSet = self[start:end]
                sys.exit(type(self).__name__ + ' ' + type(subset).__name__)

                for test_start in range(len(self)):
                    test_end = test_start + len(subset)
                    test_subset: EventSet = self[test_start:test_end]

                    if subset.is_repeat(test_subset):
                        subset._freq += 1

                subsets.append(subset)

        # Pick the subset that matches the most events for efficiency
        subset: EventSet = max(subsets, lambda subset: len(subset) * subset.freq)

        for event in subset:
            event.rrule = RecurrenceRule(
                interval=subset.delta,
                count=subset.freq
            )

            occurences: EventSet = event.occurences

            # Exceptions
            for occurence in occurences:
                if occurence not in self:
                    event.exceptions += occurence

            # Additions
            for occurence in self:
                if occurence not in occurences:
                    event.occurences += occurence

        # Mutate the EventSet in place
        self = subset

    # Determine if another EventSet is a repeat
    def is_repeat(self, other: EventSet) -> bool:
        # Ensure all corresponding events have the same delta
        delta: TimeDelta = None

        for events in zip(self, other):
            start_delta: TimeDelta = events[1].start - events[0].start
            end_delta: TimeDelta = events[1].end - events[1].end

            if start_delta != end_delta:
                return False

            if not delta:
                delta = start_delta
            elif start_delta != delta:
                return False

        self._delta: TimeDelta = delta

        return True

    # Get a subset of events
    def __getslice__(self, start: int, stop: int):
        return self.__class__(list.__getslice__(start, stop))

    def delta(self, other: EventSet):
        pass