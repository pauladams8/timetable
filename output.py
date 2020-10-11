# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from typing import List

# Pretty print a list
def human_list(items: List, conj: str = 'and') -> str:
    # Create a copy of the list so we don't mutate the original
    items = items.copy()

    # It is idiomatic in English to bridge the last 2 words with a conjuction
    items.insert(len(items) - 1, conj)

    # Lists of 2 typically follow a determiner
    if len(items) == 2:
        determiners = {
            'and': 'both',
            'or': 'either'
        }

        determiner = determiners.get(conj)

        if determiner:
            items.append(0, determiner)

    return ' '.join(items)