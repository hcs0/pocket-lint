"""An example python module for testing."""

__metaclass__ = type

__all__ = [
    'CAST',
    'is_thingumbob',
    'Snark',
    'TITLE'
    ]

import sys
from textwrap import dedent
from os import path as os_path


thingumbob = 'Thingumbob'

TITLE = 'The Hunting of The Snark'
CAST = (
    'Bellman',
    'Boots',
    'Barrister',
    'Billiard-marker',
    'Banker',
    'Beaver',
    'Baker',
    'Butcher',
    thingumbob,
    )

total_cast = len(CAST)


def is_thingumbob(name):
    """Return True is the name is synonymous with Thingumbob."""
    names = (thingumbob, "Hi", "Fry me", "Fritter my wig",
             "What-you-may-call-um", "What-was-his-name", "Thing-um-a-jig",
             "Candle-ends",  "Toasted-cheese.")
    return name in names


class Snark:
    """A class is a namespace that scopes identifiers."""
    DEFAULT_VICTIM = 'Baker'

    def __init__(self, snark_is_a_boojum=True):
        """Create the snark.
        
        :param snark_is_a_boojum: Is the snark a boojum, or a member of the
            crew.
        """
        self.snark_is_a_boojum = snark_is_a_boojum
        if snark_is_a_boojum:
            self.cast = (CAST + 'snark')

    def hunt(self):
        """Return a 2-tuple of the victim and the killer.

        Hunt the snark, or is it the other way around?
        """
        if self.snark_is_a_boojum:
            boo = 'snark'
        else:
            boo = 'Boots'
        return self.DEFAULT_VICTIM, boo


def main(argv=None):
    """Hunt the Snark."""
    file_path = os_path.abspath(__file__)
    message = dedent("""
        This is an example python module used for testing. It has no
        true value in itself. This file is located at
        %s
        """ % file_path)
    print message


if __name__ == '__main__':
    sys.exit(main(sys.argv))

