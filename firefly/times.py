# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from datetime import time as Time

# Daily recurring event
class DailyEvent():
    def __init__(self, start_time: Time, end_time: Time):
        self.start_time: Time = start_time
        self.end_time: Time = end_time

# These constants are KGS specific
BREAK: DailyEvent = DailyEvent(
    start_time=Time(10, 45),
    end_time=Time(11, 10)
)
LUNCH: DailyEvent = DailyEvent(
    start_time=Time(12, 55),
    end_time=Time(14)
)