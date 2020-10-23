# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from typing import List, Dict

# Conj - determiner lookup
_DETERMINERS: dict = {
    'and': 'both',
    'or': 'either'
}

# Pretty print a list
def human_list(items: List[str], conj: str = 'and', determiners: bool = False) -> str:
    # Create a copy of the list so we don't mutate the original
    items: List = items.copy()

    # It is idiomatic in English to bridge the last 2 words with a conjuction
    items.append(' '.join([items.pop(), conj, items.pop()]))

    # Lists of 2 can follow a determiner
    if determiners and len(items) == 2:
        determiner: str = _DETERMINERS.get(conj)

        if determiner:
            items.insert(0, determiner + ' ' + items.pop(0))

    return ', '.join(items)