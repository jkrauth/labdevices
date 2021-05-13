"""
Provides a mock for the plx_gpib_ethernet package used in the
Ando devices.
"""
from unittest.mock import Mock

# The commands that are used in the methods of the
# ANDO devices and typical responses.
QUERY_COMMANDS = {
    # Spectrum Analyzer commands
    "*IDN?":        "ANDO dummy\r\n",
    "SWEEP?":       "0\r\n",
    "SMPL?":        " 501\r\n",
    "ANA?":         " 490.808,  94.958, 19\r\n",
    "CTRWL?":       "1050.00\r\n",
    "SPAN?":        "1300.0\r\n",
    "CWPLS?":       "1\r\n",
    "PLMOD?":       "   38\r\n",
}

class PLXDummy(Mock):
    """
    Mock class for the plx_gpib_ethernet package when using the
    ANDO devices as dummy.
    """

    @staticmethod
    def query(command: str):
        """
        Containes all the query commands used in the ANDO Spectrometer
        and returns a valid string.
        """
        if command in QUERY_COMMANDS:
            return QUERY_COMMANDS[command]
        if "LDATA" in command:
            return '  20,-210.00,-210.00,-210.00,-210.00,-75.28,-210.00,-210.00,-210.00,'\
                '-210.00,-210.00,-210.00,-210.00,-210.00,-210.00,-210.00, -78.57, -70.96,'\
                ' -75.37,-210.00,-210.00\r\n'
        if "WDATA" in command:
            return '  20, 400.000, 401.300, 402.600, 403.900, 405.200, 406.500, 407.800,'\
                ' 409.100, 410.400, 411.700, 413.000, 414.300, 415.600, 416.900, 418.200,'\
                ' 419.500, 420.800, 422.100, 423.400, 424.700\r\n'
        return Mock()
