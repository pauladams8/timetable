# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .. import Command
from argparse import Namespace as Arguments

# Login to Firefly
class Login(Command):
    # The command name
    name: str = 'login'

    # The command description
    description: str = 'Login to Firefly'

    # Execute the command
    def __call__(self, args: Arguments):
        self.print_client_state(
            lambda client: client.login()
        )