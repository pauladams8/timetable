# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from typing import Type
from ..enums import Enum
from ..errors import InputError
from ..fmt import human_list, human_cls

# Parse an enum
def parse_enum(human_name: str, cls: Type[Enum], name: str = None) -> Enum:
    value: cls = cls.from_human_name(human_name)

    if not value:
        raise InputError('%s is not a valid %s. Please choose %s.' % (
                human_name,
                name or human_cls(cls),
                human_list([value.human_name for value in cls], conj='or')
            )
        )

    return value
