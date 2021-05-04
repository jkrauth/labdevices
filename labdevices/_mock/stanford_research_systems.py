"""
Provides a mock for the pyvisa package used in the
Stanford Research Systems devices.
"""
from unittest.mock import Mock

# The commands that are used in the methods of the Stanford
# Research Systems devices and typical responses.
QUERY_COMMANDS = {
    # DG device commands
    b"*IDN?\n":         b"Stanford Research Systems dummy\r\n",
}


class SocketDummy(Mock):
    """
    Mock class for the socket package when using the
    Stanford Research Systems devices as dummy.
    """

    def send(self, command: str):
        """
        Containes all the send commands used in the Stanford Research
        Systems devices and sets the correct return value for the
        recv() method.
        """
        if command in QUERY_COMMANDS:
            self.recv.return_value = QUERY_COMMANDS[command]
        elif b"DLAY?" in command:
            self.recv.return_value = b'2,+0.001000000000\r\n'
        elif b"LAMP?" in command:
            self.recv.return_value = b'+0.5\r\n'
