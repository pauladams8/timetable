# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .. import Command
from typing import List
from .search_directory import SearchDirectory

# Get the teachers
class GetTeachers(Command):
    # The command name
    name: str = 'teachers'

    # The subcommands
    subcommands: List[Command] = [
        SearchDirectory
    ]