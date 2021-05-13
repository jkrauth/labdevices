"""
Provides a mock for the socket package used in the
Applied Motion Products devices.
"""
from unittest.mock import Mock

# The commands that are used in the methods of the Applied
# Motion Products devices and typical responses.
QUERY_COMMANDS = {
    # STF03D device commands
    b'\x00\x07DI\r':   b'\x00\x07DI=20000\r', # get_future_movement_value
    b'\x00\x07MV\r':   b'\x00\x07100H179M\r',# idn
    b'\x00\x07AL\r':   b'\x00\x07AL=0100\r', # get_alarm
    b'\x00\x07SC\r':   b'\x00\x07SC=020C\r', # is_moving
    b'\x00\x07MR\r':   b'\x00\x07MR=8\r',    # get_microstep
    b'\x00\x07MC\r':   b'\x00\x07MC=1\r',    # max_current
    b'\x00\x07CI\r':   b'\x00\x07CI=0.6\r',  # idle_current
    b'\x00\x07CC\r':   b'\x00\x07CC=1\r',    # change_current
    b'\x00\x07SP\r':   b'\x00\x07SP=0\r',    # get_position
    b'\x00\x07SP0\r':  b'\x00\x07%\r',       # reset_position
    b'\x00\x07IP\r':   b'\x00\x07IP=00000000\r', # get_immediate_position
    b'\x00\x07AC\r':   b'\x00\x07AC=25\r',   # acceleration
    b'\x00\x07DE\r':   b'\x00\x07DE=25\r',   # deceleration
    b'\x00\x07VE\r':   b'\x00\x07VE=10\r',   # speed
}


class SocketDummy(Mock):
    """
    Mock class for the socket package when using the
    Stanford Research Systems devices as dummy.
    """

    def sendto(self, command: str, address: tuple):
        """
        Containes all the send commands used in the Stanford Research
        Systems devices and sets the correct return value for the
        recv() method.
        """
        _ = address
        if command in QUERY_COMMANDS:
            self.recv.return_value = QUERY_COMMANDS[command]
        else:
            # For all commands that set a number (where a number is attached to
            # the standard command) return the standard answer.
            # This answer is for now also returned in the case that a not implemented
            # command is used.
            self.recv.return_value = b'\x00\x07%\r'
