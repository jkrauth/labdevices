"""
For communication with devices from Applied Motion Products.

The IP can be set via a small wheel (S1) on the device itself.
We used the windows software 'STF Configurator' from Applied Motion
Products for the first configuration of the controller and to
give it its IP address in our local subnet.

File name: applied_motion_products.py
Author: Julian Krauth
Date created: 2020/09/02
Python Version: 3.7
"""
import socket

# The ports for communication. We usually use UDP
TCP_PORT = 7776
UDP_PORT = 7775

# IP address of host pc.
# If 0.0.0.0: Communication on all ethernet interfaces.
# When instantiating the class it is better to use
# the specific local IP address of that PC.
HOST_IP = '0.0.0.0'
HOST_PORT = 15005

ERROR_CODES = {
    0x0000: 'No alarms',
    0x0001: 'Position Limit',
    0x0002: 'CCW Limit',
    0x0004: 'CW Limit',
    0x0008: 'Over Temp',
    0x0010: 'Internal Voltage',
    0x0020: 'Over Voltage',
    0x0040: 'Under Voltage',
    0x0080: 'Over Current',
    0x0100: 'Open Motor Winding',
    0x0200: 'Bad Encoder',
    0x0400: 'Comm Error',
    0x0800: 'Bad Flash',
    0x1000: 'No Move',
    0x2000: '(not used)',
    0x4000: 'Blank Q Segment',
    0x8000: '(not used)',
}

STATUS_CODES = {
    0x0000: 'Motor disabled',
    0x0001: 'Motor enabled and in position',
    0x0002: 'Sampling (for Quick Tuner)',
    0x0004: 'Drive Fault (check Alarm Code)',
    0x0008: 'In Position (motor is in position)',
    0x0010: 'Moving (motor is moving)',
    0x0020: 'Jogging (currently in jog mode)',
    0x0040: 'Stopping (in the process of stopping from a stop command)',
    0x0080: 'Waiting (for an input; executing a WI command)',
    0x0100: 'Saving (parameter data is being saved)',
    0x0200: 'Alarm present (check Alarm Code)',
    0x0400: 'Homing (executing an SH command)',
    0x0800: 'Waiting (for time; executing a WD or WT command)',
    0x1000: 'Wizard running (Timing Wizard is running)',
    0x2000: 'Checking encoder (Timing Wizard is running)',
    0x4000: 'Q Program is running',
    0x8000: 'Initializing (happens at power up)',
}

STEPS_PER_TURN = {
    # Gives the number of steps for a full
    # motor turn, given the microstep resolution
    # setting.
    0: 200,
    1: 400,
    3: 2000,
    4: 5000,
    5: 10000,
    6: 12800,
    7: 18000,
    8: 20000,
    9: 21600,
    10:25000,
    11:25400,
    12:25600,
    13:36000,
    14:50000,
    15:50800,
}

class STF03D:
    """Class for the STF03-D Stepper Motor Controllers."""

    _header = bytes([0x00, 0x007])
    _tail = bytes([0xD])

    def __init__(self, device_ip: str, host_ip: str=HOST_IP,
        host_port: int=HOST_PORT, timeout: float=5):
        """
        Arguments:
        device_ip   -- IP address of device
        host_ip     -- IP address of host, can be 0.0.0.0
        host_port   -- Port used by host
        timeout     -- in seconds
        """
        self.device_ip = device_ip
        self.host_ip = host_ip
        self.host_port = host_port
        self.timeout = timeout
        self._device = None

        # This is the calibration and it has to be set by self.set_calibration()
        self._units_per_motor_turn = None

    def _write(self, cmd: str):
        """Send a message with the correct header and end characters"""
        to_send = self._header + cmd.encode() + self._tail
        self._device.sendto(to_send, (self.device_ip, UDP_PORT))

    def _read(self) -> str:
        """Read UDP message, decode, strip off header and end characters
        and return."""
        respons_raw = self._device.recv(1024)
        respons = respons_raw.decode()
        return respons[2:-1]

    def _query(self, cmd: str) -> str:
        self._write(cmd)
        return self._read()

    def _move_settings(self, cmd: str, value: None) -> str:
        """Base function for the set/get functionality
        of the speed setting functions."""
        if value is None:
            respons = self._query(cmd)[3:]
            return respons
        cmd = cmd + str(value)
        return self._query(cmd)

    def _distance_or_position(self, value: float=None):
        """Set or request the distance by which the motor moves after sending
        a relative move command, or the position to which the motor
        moves after sending an absolute move command.
        value -- in units as defined by the calibration.
        """
        if value is None:
            steps = int(self._move_settings('DI', None))
            value = self._step_to_unit(steps)
            return value
        steps = self._unit_to_step(value)
        print(f'Move by/to {value} degrees, equiv. to {steps} steps.')
        return self._move_settings('DI', steps)

    def initialize(self):
        """Establish connection to device."""
        self._device = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._device.bind((self.host_ip, self.host_port))
        self._device.settimeout(self.timeout)
        print(f'Connected to rotary feedthrough with IP={self.device_ip}.')

    def set_calibration(self, units_per_motor_turn: float):
        """
        Arguments:
        units_per_motor_turn -- units could be degree or meter.
                                Example:
                                For a rotation stage with gear ratio 1/96 the
                                conversion factor into degrees would be 360/96,
                                For a linear stage it would be the lead value of the screw.
        """
        self._units_per_motor_turn = units_per_motor_turn

    def close(self):
        """Close connection to device."""
        if self._device is None:
            print('Device is already closed.')
            return
        self._device.close()
        print(f'Closed rotary feedthrough with IP={self.device_ip}.')


    def get_alarm(self) -> list:
        """Reads back an equivalent hexadecimal value of the
        Alarm Code's 16-bit binary word and translates it into
        corresponding error messages.
        """
        # Strip off the 'AL=' prefix
        respons = self._query('AL')[3:]
        # Convert hex string to integer
        alarm = int(respons, 16)
        error_list = []
        if not alarm:
            error_list.append(ERROR_CODES[alarm])
        else:
            for key, val in ERROR_CODES.items():
                if key & alarm:
                    error_list.append(val)
        return error_list

    def get_status(self) -> list:
        """Reads back an equivalent hexadecimal value of the
        Status Code's 16-bit binary word and translates it into
        corresponding status messages.
        """
        # Strip off the 'SC=' prefix
        respons = self._query('SC')[3:]
        status = int(respons, 16)
        status_list = []
        if not status:
            status_list.append(STATUS_CODES[status])
        else:
            for key, val in STATUS_CODES.items():
                if key & status:
                    status_list.append(val)
        return status_list

    def is_moving(self) -> bool:
        """Ask for device movement status, return boolean."""
        respons = self._query('SC')[3:]
        status = int(respons, 16)
        return bool(0x0010 & status)

    def get_microstep(self) -> int:
        """Requests the microstep resolution of the drive."""
        respons = self._move_settings('MR', None)
        return int(respons)

    def set_microstep(self, value: int=3) -> None:
        """Sets or requests the microstep resolution of the drive.
        Argument:
        value -- between [0 and 15] (standard is 3)
        """
        _ = self._move_settings('MR', value)

    @property
    def conversion_factor(self) -> float:
        """This yields the steps/user-defined-unit ratio. The steps of the
        stepper motor depend on the microstep resolution setting.
        """
        if self._units_per_motor_turn is None:
            raise Exception('Set calibration first')
        steps_per_motor_turn = STEPS_PER_TURN[self.get_microstep()]
        steps_per_unit = float(steps_per_motor_turn) / float(self._units_per_motor_turn)
        return steps_per_unit

    def _step_to_unit(self, step: int) -> float:
        """Convert stepper motor steps into user-defined units."""
        return float(step) / self.conversion_factor

    def _unit_to_step(self, value: float) -> int:
        """Convert value in user-defined units into
        steps of the stepper motor.
        Argument:
        value -- in user-defined units"""
        return int(round(value * self.conversion_factor))

    def max_current(self, value: float=None):
        """Set or request the maximum idle and change current limit.
        value -- in Ampere, max is 3 A"""
        return self._move_settings('MC', value)

    def idle_current(self, value: float=None):
        """Set or request the current the standing still situation.
        A good value seems to be 0.5 A.
        value -- in Ampere, max is given by self.max_current()."""
        return self._move_settings('CI', value)

    def change_current(self, value: float=None):
        """Set or request the current for moving the stepper motor.
        For not missing any steps that should be as high as possible,
        which in this case is 3 A.
        value -- in Ampere, max is given by self.max_current()."""
        return self._move_settings('CC', value)

    def get_position(self) -> float:
        """Returns the current position in user-defined units."""
        steps = int(self._query('SP')[3:])
        print(f'Position in steps is: {steps}')
        return self._step_to_unit(steps)

    def reset_position(self):
        """Set current motor position to the new zero position."""
        _ = self._query('SP0')

    def get_immediate_position(self) -> int:
        """This returns the calculated trajectory position, which
        is not always equal to the actual position.
        Units are stepper motor steps.
        """
        respons = self._query('IP')[3:]
        print(respons)
        position = int(respons, 16)
        return position

    def acceleration(self, value: float=None):
        """Sets or requests the acceleration used
        in point-to-point move commands.
        Argument:
        value -- in rps/s (a standard value is 1)
        """
        return self._move_settings('AC', value)

    def deceleration(self, value: float=None):
        """Sets or requests the deceleration used
        in point-to-point move commands
        Argument:
        value -- in rps/s (a standard value is 1)
        """
        return self._move_settings('DE', value)

    def speed(self, value: float=None):
        """Sets or requests shaft speed for point-to-point
        move commands
        Argument:
        value -- in rps (a standard value is 2)
        """
        return self._move_settings('VE', value)

    def move_relative(self, value: float):
        """Relative rotation of the feedthrough
        Argument:
        value -- in user-defined units
        """
        _ = self._distance_or_position(value)
        _ = self._query('FL')

    def move_absolute(self, position: float):
        """Rotate the feedthrough to a given position
        Argument:
        position -- in degrees
        """
        _ = self._distance_or_position(position)
        _ = self._query('FP')


class STF03DDummy:
    """Class for testing. Does not actually connect to any device."""
    def __init__(self, device_ip, host_ip=HOST_IP,
        host_port=HOST_PORT, timeout=5):

        self.device_ip = device_ip
        self.host_ip = host_ip
        self.host_port = host_port
        self.timeout = timeout
        # Dummy parameters
        self.position = 0
        self.accel = 1
        self.decel = 1
        self.velocity = 1

    def initialize(self):
        pass

    def close(self):
        pass

    def get_alarm_code(self):
        return ['no alarms']

    def get_position(self):
        return self.position

    def reset_position(self):
        self.position = 0

    def get_immediate_position(self):
        return self.position

    def acceleration(self, value: float=None):
        if value is None:
            return self.accel
        self.accel = value
        return ''

    def deceleration(self, value: float=None):
        if value is None:
            return self.decel
        self.decel = value
        return ''

    def speed(self, value: float=None):
        if value is None:
            return self.velocity
        self.velocity = value
        return ''

    def move_relative(self, value: float):
        self.position += value

    def move_absolute(self, position: float):
        self.position = position
