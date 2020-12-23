# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .. import Command
from typing import List
from colorama import Style
from firefly import Teacher
from firefly.fmt import human_list
from argparse import Namespace as Arguments

# Search the school directory by surname
class SearchDirectory(Command):
    # The command name
    name: str = 'search'

    # The command description
    description: str = 'Search the school directory by surname'

    # Register the command arguments
    def register_arguments(self):
        self.parser.add_argument('--surname', help='The surname to search for')

    # Execute the command
    def __call__(self, args: Arguments):
        surname: str = self.arg_or_ask('surname')

        teachers: List[Teacher] = self.print_client_state(
            lambda client: client.search_directory(surname)
        )

        if not teachers:
            print('No results found')

        for teacher in teachers:
            print(Style.BRIGHT + teacher.name + Style.RESET_ALL)
            if teacher.roles:
                print(Style.DIM + '\n'.join(teacher.roles) + Style.RESET_ALL)
            if teacher.email_address:
                print('📪', teacher.email_address)
            if teacher.phone_number:
                print('📞', teacher.phone_number)
            if teacher.departments:
                print('Works in', human_list(teacher.departments))