# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

import re
from typing import Type
from firefly import Enum
from output import human_list

# Parse an enum
def parse_enum(human_name: str, cls: Type[Enum], name: str = None) -> Enum:
    value: cls = cls.from_human_name(human_name)

    if not value:
        raise ValueError('%s is not a valid %s. Please choose %s.' % (
                human_name,
                name or re.sub(r'(\w)([A-Z])', lambda match: match[1] + ' ' + match[2], cls.__name__).lower(),
                human_list([value.human_name for value in cls], conj='or')
            )
        )

    return value
