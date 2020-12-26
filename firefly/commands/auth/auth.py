# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .. import Command
from typing import List
from .login import Login
from .logout import Logout
from argparse import Namespace as Arguments

# Auth command group
class Auth(Command):
    # The command name
    name: str = 'auth'

    # The command description
    description: str = 'Authentication commands. Please choose either `login` or `logout`.'

    # The subcommands
    subcommands: List[Command] = [
        Login,
        Logout
    ]