# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .. import Command
from argparse import Namespace as Arguments

# Logout from Firefly
class Logout(Command):
    # The command name
    name: str = 'logout'

    # The command description
    description: str = 'Logout from Firefly'

    # Execute the command
    def __call__(self, args: Arguments):
        self.print_client_state(
            lambda client: client.logout()
        )