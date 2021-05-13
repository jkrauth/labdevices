"""
Provides a mock for the pyvisa package used in the
Newport devices.
"""
from unittest.mock import Mock

# The commands that are used in the methods of the
# Newport devices and typical responses.
QUERY_COMMANDS = {
    # SMC100 commands
    "1ID?":     "1IDTRA25CC_PN:B183906_UD:18114",
    "1TS":      "1TS01000A",
    "1TE":      "1TE@",
    "1PA?":     "1PA0",
    "1VA?":     "1VA0.4",
    "1AC?":     "1AC1.6",
}

class PyvisaDummy(Mock):
    """
    Mock class for the pyvisa package when using the
    Newport devices as dummy.
    """

    @staticmethod
    def query(command: str):
        """
        Containes all the query commands used in the Newport SMC100
        and returns a valid string.
        """
        if command in QUERY_COMMANDS:
            return QUERY_COMMANDS[command]
        return Mock()
