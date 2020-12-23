# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import re
from typing import List, Dict, Generator, Type
from datetime import date as Date, timedelta as TimeDelta

# Pretty print a list
def human_list(items: List[str], conj: str = 'and', determiners: bool = False) -> str:
    # Create a copy of the list so we don't mutate the original
    items = items.copy()

    # It is idiomatic in English to bridge the last 2 words with a conjuction
    if len(items) > 1:
        items.append(' '.join([items.pop(-2), conj, items.pop()]))

    # Lists of 2 can follow a determiner
    if determiners and len(items) == 2:
        determiner: str = {
            'and': 'both',
            'or': 'either'
        }.get(conj)

        if determiner:
            items.insert(0, determiner + ' ' + items.pop(0))

    return ', '.join(items)

# Pretty print a datetime.timedelta
def human_timedelta(delta: TimeDelta) -> str:
    units: Dict[str, int] = {
        'microsecond': delta.microseconds,
        'second': delta.seconds,
        'day': delta.days,
    }

    units['week'] = units['day'] / 7
    units['month'] = units['day'] / 30
    units['year'] = units['month'] / 12
    units['decade'] = units['year'] / 10
    units['century'] = units['decade'] / 10
    units['millenium'] = units['century'] / 10
    # The homework is very overdue by this point, it's probably ok to stop as edge cases are unlikely.

    # Generates absolute unit tuples
    def abs_unit() -> Generator:
        for k, v in units.items():
            v = abs(v)
            if v >= 1:
                yield [k, v]

    try:
        [k, v] = sorted(abs_unit(), key=lambda unit: unit[1])[0]
    except IndexError:
        return None

    v = round(v)

    plurals: Dict[str, str] = {
        'century': 'centuries',
        'millenium': 'millenia'
    }

    return str(v) + ' ' + (k if v == 1 else plurals.get(k) or k + 's')

# Pretty print a datetime.date
def human_date(date: Date) -> str:
    delta: TimeDelta = date - Date.today()

    try:
        if delta.total_seconds() < 0:
            if delta.days == -1:
                return 'yesterday'
            return human_timedelta(delta) + ' ago'
        if delta.days == 0:
            return 'today'
        if delta.days == 1:
            return 'tomorrow'
        return 'in ' + human_timedelta(delta)
    except TypeError:
        raise Exception('None timedelta')

# Pretty print a class name
def human_cls(cls: Type) -> str:
    return re.sub(r'(?<!^)([A-Z][a-z])', lambda match: ' ' + match[1], cls.__name__).lower()

# Emojify a warning
def warn(e: str):
    return '⚠️ ' + e