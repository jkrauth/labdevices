"""
Provides a mock for the pyvisa package used in the
thorlabs devices.
"""
from unittest.mock import Mock

# The commands that are used in the methods of the
# Thorlabs devices and typical responses.
QUERY_COMMANDS = {
    # TSP01 commands
    "*IDN?":                    "Thorlabs,TSP01,M00416749,1.2.0",
    ":READ?":                   [23.973883],
    ":SENSe2:HUMidity:DATA?":   [25.24333],
    ":SENSe3:TEMPerature:DATA?":[21.78577],
    ":SENSe4:TEMPerature:DATA?":[21.43771],
}

class PyvisaDummy(Mock):
    """
    Mock class for the pyvisa package when using the
    Thorlabs devices as dummy.
    """

    @staticmethod
    def query(command: str):
        """
        Containes all the query commands used in the Thorlabs TSP01
        and returns a valid string.
        For unknown commands a Mock object is returned.
        """
        if command in QUERY_COMMANDS:
            return QUERY_COMMANDS[command]
        return Mock()

    def query_ascii_values(self, command: str):
        """ Does the same job as query, but is needed,
        because the two methods are used in the TSP01 class. """
        return self.query(command)
