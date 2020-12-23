# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .error import FireflyError

# Raised when the user supplies invalid data to the client
class InputError(FireflyError):
    pass