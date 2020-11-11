"""
For communication with devices from Applied Motion Products.
We currently use the STF03-D Stepper Motor Controllers for our
rotary feedthroughs.

The IP can be set via a small wheel (S1) on the device itself.
We used the windows software 'STF Configurator' from Applied Motion
Products for the first configuration of the controller and to
give it its IP address in our local subnet. 
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

class STF03D:

    error_codes = {
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

    status_codes = {
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

    steps_per_turn = {
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

    def __init__(
            self,
            device_ip,
            host_ip=HOST_IP,
            host_port=HOST_PORT,
            timeout=5
    ):
        self.ip = device_ip
        self.host_ip = host_ip
        self.host_port = host_port
        self.timeout = timeout
        self.sock = None

    def _write(self, cmd: str):
        """Send a message with the correct header and end characters"""
        header = bytes([0x00, 0x007])
        end = bytes([0xD])
        to_send = header + cmd.encode() + end
        self.sock.sendto(to_send, (self.ip, UDP_PORT))

    def _read(self) -> str:
        """Read UDP message, decode, strip off header and end characters
        and return."""
        respons_raw = self.sock.recv(1024)
        respons = respons_raw.decode()
        return respons[2:-1]

    def _move_settings(self, cmd: str, value: None):
        """Base function for the set/get functionality
        of the speed setting functions."""
        if value is None:
            return self.query(cmd)[3:]
        else:
            cmd = cmd + str(value)
            return self.query(cmd)

    def _distance_or_position(self, angle: float=None):
        """Set or request the distance by which the motor moves after sending
        a relative move command, or the position to which the motor
        moves after sending an absolute move command.
        angle -- in degrees.
        """
        if angle is None:
            steps = int(self._move_settings('DI', None))
            angle = self.step_to_angle(steps)
            return angle
        else:
            steps = self.angle_to_step(angle)
            print(f'Move by/to {angle} degrees, equiv. to {steps} steps.')
            return self._move_settings('DI', steps)

    def initialize(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host_ip, self.host_port))
        self.sock.settimeout(self.timeout)
        print(f'Connected to rotary feedthrough with IP={self.ip}.')

    def close(self):
        if self.sock is not None:
            self.sock.close()
            print(f'Closed rotary feedthrough with IP={self.ip}.')
        else:
            print(f'Device is already closed.')

    def query(self, cmd: str) -> str:
        self._write(cmd)
        return self._read()

    def get_alarm(self) -> list:
        """Reads back an equivalent hexadecimal value of the 
        Alarm Code's 16-bit binary word and translates it into
        corresponding error messages.
        """
        # Strip off the 'AL=' prefix
        respons = self.query('AL')[3:]
        # Convert hex string to integer
        alarm = int(respons, 16)
        error_list = []
        if not alarm: error_list.append(self.error_codes[alarm])
        else:
            for key, val in self.error_codes.items():
                if key & alarm:
                    error_list.append(val)
        return error_list

    def get_status(self) -> list:
        """Reads back an equivalent hexadecimal value of the
        Status Code's 16-bit binary word and translates it into
        corresponding status messages.
        """
        # Strip off the 'SC=' prefix
        respons = self.query('SC')[3:]
        status = int(respons, 16)
        status_list = []
        if not status: status_list.append(self.status_codes[status])
        else:
            for key, val in self.status_codes.items():
                if key & status:
                    status_list.append(val)
        return status_list

    def is_moving(self) -> bool:
        respons = self.query('SC')[3:]
        status = int(respons, 16)
        if 0x0010 & status: return True
        else: return False

    def microstep(self, value: int=None) -> int:
        """Sets or requests the microstep resolution of the drive.
        Argument:
        value -- between [0 and 15] (standard is 8)
        """
        return int(self._move_settings('MR', value))

    @property
    def conversion_factor(self):
        """This yields the steps/rotation-angle ratio. The steps of the
        stepper motor depend on the microstep resolution setting.
        The rotation angle is the one of the rotary feedthrough."""
        wormwheel_ratio = 96/1
        steps_per_motor_turn = self.steps_per_turn[self.microstep()]
        conversion_factor = float(wormwheel_ratio) * float(steps_per_motor_turn) / 360.
        return conversion_factor

    def step_to_angle(self, step: int) -> float:
        """Convert stepper motor steps into a rotation angle 
        of the rotary feedthrough."""
        return float(step) / self.conversion_factor

    def angle_to_step(self, angle: float) -> int:
        """Convert an angle of the rotary feedthrough into
        steps of the stepper motor."""
        return int(round(angle * self.conversion_factor))

    def get_position(self) -> float:
        """Returns the current angle of the rotary feedthrough in degrees."""
        steps = int(self.query('SP')[3:])
        print(f'Position in steps is: {steps}')
        return self.step_to_angle(steps)

    def reset_position(self):
        """Set current motor position to the new zero position."""
        _ = self.query('SP0')

    def get_immediate_position(self) -> int:
        """This returns the calculated trajectory position, which
        is not always equal to the actual position.
        Units are stepper motor steps.
        """
        respons = self.query('IP')[3:]
        print(respons)
        position = int(respons, 16)
        return position

    def acceleration(self, value: float=None):
        """Sets or requests the acceleration used 
        in point-to-point move commands.
        Argument:
        value -- in rps/s (a standard value is 25)
        """
        return self._move_settings('AC', value)

    def deceleration(self, value: float=None):
        """Sets or requests the deceleration used 
        in point-to-point move commands
        Argument:
        value -- in rps/s (a standard value is 25)
        """
        return self._move_settings('DE', value)        

    def speed(self, value: float=None):
        """Sets or requests shaft speed for point-to-point 
        move commands
        Argument:
        value -- in rps (a standard value is 10)        
        """
        return self._move_settings('VE', value)

    def move_relative(self, angle: float):
        """Relative rotation of the feedthrough
        Argument:
        angle -- in degrees
        """
        _ = self._distance_or_position(angle)
        _ = self.query('FL')

    def move_absolute(self, position: float):
        """Rotate the feedthrough to a given position
        Argument:
        position -- in degrees
        """
        _ = self._distance_or_position(position)
        _ = self.query('FP')


class STF03DDUMMY:
    def __init__(
            self,
            device_ip,
            host_ip=HOST_IP,
            host_port=HOST_PORT,
            timeout=5
    ):
        self.ip = device_ip
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
        else:
            self.accel = value
            return ''

    def deceleration(self, value: float=None):
        if value is None:
            return self.decel
        else:
            self.decel = value
            return ''

    def speed(self, value: float=None):
        if value is None:
            return self.velocity
        else:
            self.velocity = value
            return ''

    def move_relative(self, angle: float):
        self.position += angle

    def move_absolute(self, position: float):
        self.position = position