# Copyright Paul Adams, 2020. All rights reserved.
# Unauthorized reproduction is prohibited.

from .fmt import warn

# Ask for input
def ask(prompt: str) -> str:
    value = input(prompt + ': ')

    if not value:
        print(warn('Please supply a value or press ctrl+c to exit'))
        # Try again
        return ask(prompt)

    return value