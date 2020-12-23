# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .error import FireflyError

# Raised when the client is unable to authenticate
class AuthenticationError(FireflyError):
    pass