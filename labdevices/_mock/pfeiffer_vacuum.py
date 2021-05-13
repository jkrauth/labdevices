"""
Provides a mock for the pyvisa package used in the
Pfeiffer Vacuum devices.
"""
from unittest.mock import Mock

# The commands that are used in the methods of the
# Pfeiffer Vacuum devices and typical responses.
QUERY_COMMANDS = {
    # TPG362 commands
    "AYT":     "TPG362,PTG28290,44998061,010300,010100",
    "ERR":     "0000",
    "PR1":     "5,+0.0000E+00",
    "PR2":     "5,+0.0000E+00",
    "PRX":     "5,+0.0000E+00,5,+0.0000E+00",
    "UNI":     "4",
    "TMP":     "23",
}

class PyvisaDummy(Mock):
    """
    Mock class for the pyvisa package when using the
    Pfeiffer Vacuum devices as dummy.
    """

    def query(self, command: str):
        """
        Containes all the query commands used in the Pfeiffer Vacuum TPG362
        and returns a valid string.
        """
        if command in QUERY_COMMANDS:
            self.response_value.return_value = QUERY_COMMANDS[command]
            return chr(6)
        if command == chr(5):
            return self.response_value()
        return Mock()
