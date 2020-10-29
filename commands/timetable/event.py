# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from __future__ import annotations

from collections import Counter
from typing import List, Dict, Tuple
from datetime import datetime as DateTime, timedelta as TimeDelta

# Instance of an event
class Occurence():
    # Create an instance
    def __init__(self, start: DateTime, end: DateTime):
        self.start: DateTime = start
        self.end: DateTime = end

    # Get the duration
    @property
    def duration(self) -> TimeDelta:
        return self.end - self.start

# Set of occurences
class OccurenceSet():
    # Create an instance
    def __init__(self, occurences: List[Occurence], rrule: RecurrenceRule = None, exceptions: List[Occurence] = None):
        self._occurences: List[Occurence] = occurences or []
        self._rrule: RecurrenceRule = rrule
        self._exceptions: List[Occurence] = exceptions or []

    # Compute all occurences
    @property
    def occurences(self):
        occurences: List[Occurence] = self._occurences.copy()

        for occurence in self._rrule.occurences():
            if occurence not in occurences:
                occurences.append(occurence)

        return occurences - self.exceptions

    # Compute all exceptions
    @property
    def exceptions(self):
        return self._exceptions

    # Compute the recurrence rule, removing occurences that satisfy it
    @property
    def rrule(self):
        if not self._rrule:
            rrules: List[RecurrenceRule] = []

            for start in range(len(self._occurences)):
                for end in range(len(self._occurences[start:])):
                    subset: OccurenceSet = OccurenceSet(self._occurences[start:end])
                    rrule: RecurrenceRule = RecurrenceRule(matches=subset)
                    for test_start in range(len(self._occurences)):
                        test_end = test_start + len(subset)
                        test_subset: OccurenceSet = OccurenceSet(self._occurences[test_start:test_end])
                        if subset.is_repeat(test_subset):
                            rrule.matches.extend(subset.occurences)
                    rrules.append(rrule)

            rrule: RecurrenceRule = max(rrules, lambda rrule: len(rrule.matches))

            for occurence in rrule.occurences:
                if occurence not in self._occurences:
                    self._exceptions.append(occurence)

            for match in rrule.matches:
                self._occurences.remove(match)

            self._rrule = rrule

        return self._rrule

    # Compute the length of the occurence set
    def __len__(self) -> int:
        return len(self.occurences)

    # Extend the occurence set
    def extend(self, occurences: List[Occurence]):
        self.occurences.extend(occurences)

    # Determine if another OccurenceSet is a repeat
    def is_repeat(self, other: OccurenceSet) -> bool:
        # Ensure all corresponding occurences have the same delta
        delta: TimeDelta = None

        for occurences in zip(self.occurences, other.occurences):
            start_delta: TimeDelta = occurences[1].start - occurences[0].start
            end_delta: TimeDelta = occurences[1].end - occurences[1].end

            if start_delta != end_delta:
                return False

            if not delta:
                delta = start_delta
            elif start_delta != delta:
                return False

        return True

# Rule to generate occurences
class RecurrenceRule():
    # Create an instance
    def __init__(self, matches: OccurenceSet, events: List[Event] = None):
        self.matches: OccurenceSet = matches

# Event class
class Event():
    # Create an instance
    def __init__(
        self,
        occurences: OccurenceSet,
        title: str = None,
        location: str = None,
    ):
        self.title: str = title
        self.location: str = location
        self._occurences: OccurenceSet = occurences