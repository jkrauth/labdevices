"""
Driver for the Newport motorized translation stages connected
to the SMC100 controller.
Commands and settings for serial communication are found in
the SMC100 Newport Manual

File name: newport.py
Author: Julian Krauth
Date created: 2019/05/22
Python Version: 3.7
"""
from time import sleep
from typing import Tuple
import pyvisa as visa

from ._mock.newport import PyvisaDummy

CTRL_STATUS = {
    'configuration':      0x14,
    'moving':             0x28,
    'ready from homing':  0x32,
    'ready from moving':  0x33,
    'ready from disable': 0x34,
    'ready from jogging': 0x35,
}

ERROR_CODE = {
    '@': 'No error',
    'A': 'Unknown message code or floating point controller address',
    'B': 'Controller address not correct',
    'C': 'Parameter missing or out of range',
    'D': 'Execution not allowed',
    'E': 'Home sequence already started',
    'F': 'ESP stage name unknown',
    'G': 'Displacement out of limits',
    'H': 'Execution not allowed in NOT REFERENCED state',
    'I': 'Execution not allowed in CONFIGURATION state',
    'J': 'Execution not allowed in DISABLE state',
    'K': 'Execution not allowed in READY state',
    'L': 'Execution not allowed in HOMING state',
    'M': 'Execution not allowed in MOVING state',
    'N': 'Current position out of software limit',
    'S': 'Communication Time Out',
    'U': 'Error during EEPROM access',
    'V': 'Error during command execution',
    'W': 'Command not allowed for SMC100PP version',
    'X': 'Command not allowed for CC version',
}

class SMC100:
    """Class for a controller device for positioners.

    It works via a USB connection.
    """

    defaults = {
        'write_termination':    '\r\n',
        'read_termination':     '\r\n',
        'encoding':             'ascii',
        'baud_rate':             921600,
        'timeout':              100,
        'parity':               visa.constants.Parity.none,
        'data_bits':            8,
        'stop_bits':            visa.constants.StopBits.one,
        'flow_control':         visa.constants.VI_ASRL_FLOW_XON_XOFF,
    }


    def __init__(self, port: str, dev_number: int=1):
        """
        Arguments:
        port -- address of device, e.g. /dev/ttyUSB0
        dev_number -- if SMC100 is not chained, this is typically 1.
        """
        self.port = port
        self.dev_number = dev_number
        self._device = None
        self.error_code = ERROR_CODE


    def initialize(self) -> None:
        """Connect to device."""
        port = 'ASRL'+self.port+'::INSTR'
        #rm_list = rm.list_resources()
        self._device = visa.ResourceManager('@py').open_resource(
            port,
            timeout=self.defaults['timeout'],
            encoding=self.defaults['encoding'],
            parity=self.defaults['parity'],
            baud_rate=self.defaults['baud_rate'],
            data_bits=self.defaults['data_bits'],
            stop_bits=self.defaults['stop_bits'],
            flow_control=self.defaults['flow_control'],
            write_termination=self.defaults['write_termination'],
            read_termination=self.defaults['read_termination'],
        )

        # make sure connection is established before doing anything else
        sleep(0.5)
        print(f"Connected to Newport stage {self.dev_number}: {self.idn}")

        #err, ctrl = self.error_and_controller_status() # clears error buffer
        #print(err, ctrl)
        #print("Connected to Newport stage: %s".format(self.idn))

    def write(self, cmd: str):
        """ Add device number to command and send to device. """
        cmd = f"{self.dev_number}{cmd}"
        self._device.write(cmd)

    def query(self, cmd: str) -> str:
        """ Query device. """
        # Add device number to command
        cmd_complete = f"{self.dev_number}{cmd}"
        respons = self._device.query(cmd_complete)
        # respons is build the following way:
        # dev_number+cmd_return+answer | cmd_return never contains the question mark
        #dev_number = int(respons[0])
        #cmd_return = respons[1:3]
        answer = respons[3:]

        return answer

    def close(self):
        """Close connection to device."""
        if self._device is not None:
            self._device.close()
            return
        print('Newport device is already closed')

    @property
    def idn(self) -> str:
        """ Ask for identity. """
        idn = self.query("ID?")
        return idn

    @property
    def is_moving(self) -> bool:
        """ Check if device is moving. """
        moving = CTRL_STATUS['moving']
         # get controller status and convert hex string to int
        ctrl_status = int(self.error_and_controller_status()[1], 16)
        return ctrl_status == moving

    def wait_move_finish(self, interval: float):
        """
        Arguments:
        interval -- in seconds"""
        while self.is_moving:
            sleep(interval)
        print("Movement finished")

    def error_and_controller_status(self) -> Tuple[str, str]:
        """Returns positioner errors and controller status
        in hex.
        This method also clears the error buffer.
        """
        respons = self.query('TS')
        positioner_errors = respons[0:4]
        controller_state = respons[4:6]
        return positioner_errors, controller_state

    def get_last_command_error(self) -> str:
        """When a command is not executable, an error will be memorized.
        This error can be read with this command.
        The error buffer then gets erased.
        The meaning of the error code can be translated with self.error_code.
        """
        respons = self.query('TE')
        return respons

    def move_rel(self, distance: float):
        """Move stage to new relative position.
        Arguments:
        distance -- in the stage's units.
        """
        self.write(f'PR{distance}')

    def move_abs(self, position: float):
        """Move stage to new absolute position.
        Arguments:
        position -- in the stage's units.
        """
        self.write(f'PA{position}')

    @property
    def position(self) -> float:
        """Get current position of stage."""
        pos = self.query("PA?")
        return float(pos)

    def home(self):
        """ Move device to home position. """
        self.write('OR')

    def reset(self):
        """Resetting the controller.
        After execution controller is in NOT REFERENCED state
        """
        self.write('RS')

    @property
    def speed(self) -> float:
        """ Constant moving speed of the device. """
        speed = self.query("VA?")
        return float(speed)

    @speed.setter
    def speed(self, value: float):
        self.write(f'VA{value}')

    @property
    def acceleration(self) -> float:
        """ Acceleration and deceleration of the device. """
        accel = self.query("AC?")
        return float(accel)

    @acceleration.setter
    def acceleration(self, value: float):
        self.write(f'AC{value}')

class SMC100Dummy(SMC100):
    """For testing purpose only"""

    def initialize(self) -> None:
        """Connect to dummy device."""
        self._device = PyvisaDummy()

        print(f"Connected to Newport stage {self.dev_number}: {self.idn}")


if __name__ == "__main__":

    print("This is the Conroller Driver example for the Newport Positioner.")
    PORT = '/dev/ttyUSB0'
    DEV_ID = 1
    dev = SMC100(PORT, DEV_ID)
    dev.initialize()
    #Do commands here
    dev.close()
