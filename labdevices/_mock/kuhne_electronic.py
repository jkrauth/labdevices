"""
Provides a mock for the pyvisa package used in the
Newport devices.
"""
from unittest.mock import Mock

# The commands that are used in the methods of the
# NKuhne Electronic devices and typical responses.
# QUERY commands and WRITE commands are all used in
# the query() method, but WRITE commands always return
# the string 'A'
QUERY_COMMANDS = {
    # LocalOscillator commands
    "sa":     "???",
}

WRITE_COMMANDS = ['GF1', 'MF1', 'kF1', 'HF1']

class PyvisaDummy(Mock):
    """
    Mock class for the pyvisa package when using the
    Kuhne Electronic devices as dummy.
    """

    @staticmethod
    def query(command: str):
        """
        Containes all the query commands used in the Kuhne Electronic LocalOscillator
        and returns a valid string.
        """
        if command in QUERY_COMMANDS:
            return QUERY_COMMANDS[command]
        for each in WRITE_COMMANDS:
            if each in command:
                return 'A'
        return Mock()
