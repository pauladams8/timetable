# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .error import FireflyError

# Raised when the client is unable to parse the config file
class ConfigError(FireflyError):
    pass