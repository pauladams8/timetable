# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from datetime import time as Time

# Daily recurring event
class DailyEvent():
    # Create an instance
    def __init__(self, start: Time, end: Time):
        self.start: Time = start
        self.end: Time = end

# These constants are KGS specific
BREAK: DailyEvent = DailyEvent(
    start=Time(10, 45),
    end=Time(11, 10)
)
LUNCH: DailyEvent = DailyEvent(
    start=Time(12, 55),
    end=Time(14)
)