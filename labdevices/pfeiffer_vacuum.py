"""
Driver for the Pfeiffer Vacuum Dual Gauge TPG 362

Currently only works with a USB connection.
According to a phone call with a Pfeiffer technician,
the ethernet connection should work via port number 8000.
Unfortunately this currently doesn't work. I am not sure why.
The guy said that there were some problems with the port
and that they were fixed with
firmware 010500 (currently installed is 010300).
So, in order to use the ethernet communication we might try to
install the latest firmware on it.

File name: pfeiffer_vacuum.py
Author: Julian Krauth
Date created: 2020/08/25
Python version: 3.7
"""
import time
import pyvisa

CTRL_CHAR = {
    'ETX': chr(3), # end of text / clear input buffer
    'ACK': chr(6), # positive acknowledge
    'ENQ': chr(5), # enquiry
    'NAK': chr(21), # negative acknowledge
}
ERRORS = {
    '0000': 'No error',
    '1000': 'ERROR (see display)',
    '0100': 'No hardware error!',
    '0010': 'Inadmissible parameter error',
    '0001': 'Syntax error',
}
MEASUREMENT_STATUS = {
    0: 'Measurement data okay',
    1: 'Underrange',
    2: 'Overrange',
    3: 'Sensor error',
    4: 'Sensor off (IKR, PKR, IMR, PBR)',
    5: 'No sensor (output: 5,2.0000E-2 [mbar])',
    6: 'Identification error',
}
PRESSURE_UNITS = {
    0: 'mbar/bar',
    1: 'Torr',
    2: 'Pascal',
    3: 'Micron',
    4: 'hPascal',
    5: 'Vold',
}

class TPG362:
    """Driver for the TPG362 Pfeiffer Vacuum Dual Gauge
    Works currently only with USB connection.

    It might also work for other/older dual gauge versions
    of pfeiffer.
    """

    def __init__(self, port='/dev/ttyUSB0'):
        self.addr = 'ASRL'+port+'::INSTR'
        #self.addr = 'TCPIP0::10.0.0.110::5025::SOCKET'
        self._device = None

    def initialize(self):
        """Connect to device."""
        self._device = pyvisa.ResourceManager().open_resource(
            self.addr,
            timeout=100,
            encoding='ascii',
            parity=pyvisa.constants.Parity.none,
            baud_rate=9600,
            data_bits=8,
            stop_bits=pyvisa.constants.StopBits.one,
            flow_control=pyvisa.constants.VI_ASRL_FLOW_NONE,
            write_termination='\r\n',
            read_termination='\r\n',
        )

    def close(self):
        """Close connection to device."""
        if self._device is not None:
            self._device.close()

    def _send_command(self, cmd: str):
        recv = self._device.query(cmd)
        if recv ==  CTRL_CHAR['NAK']:
            message = 'Serial communication returned negative acknowledge'
            raise IOError(message)
        if recv != CTRL_CHAR['ACK']:
            message = f'Serial communication returned unknown response: {recv}'
    def _get_data(self):
        data = self._device.query(CTRL_CHAR['ENQ'])
        return data

    def _query(self, cmd: str):
        self._send_command(cmd)
        data = self._get_data()
        _ = self._clear_output_buffer()
        return data

    def _clear_output_buffer(self):
        """Clear the output buffer"""
        time.sleep(0.1)
        just_read = self._device.read()
        return just_read

    def idn(self):
        cmd = 'AYT'
        response = self._query(cmd).split(',')
        result = {
            'Type': response[0],
            'Model No.': response[1],
            'Serial No.': response[2],
            'Firmware version': response[3],
            'Hardware version': response[4],
        }
        return result


    def error_status(self):
        """
        Returns error status
        """
        cmd = 'ERR'
        response = self._query(cmd)
        return response, ERRORS[response]

    def pressure_gauge(self, gauge: int):
        """Returns pressure and measurement status for gauge X.

        Arg:
        gauge -- int, 1 or 2
        """
        if gauge not in [1, 2]:
            message = 'The input gauge number can only be 1 or 2'
            raise ValueError(message)

        cmd = 'PR'+ str(gauge)
        response = self._query(cmd).split(',')
        status_code = int(response[0])
        value = float(response[1])
        return value, (status_code, MEASUREMENT_STATUS[status_code])

    def pressure_gauges(self):
        """Returns tuple with pressure and measurement status
        for the two gauges."""
        cmd = 'PRX'
        response = self._query(cmd).split(',')
        # The reply is on the form: x,sx.xxxxEsxx,y,sy.yyyyEsyy
        status_code1 = int(response[0])
        value1 = float(response[1])
        status_code2 = int(response[2])
        value2 = float(response[3])
        return (value1, (status_code1, MEASUREMENT_STATUS[status_code1]),
                value2, (status_code2, MEASUREMENT_STATUS[status_code2]))

    def pressure_unit(self) -> str:
        """Return the pressure unit"""
        cmd = 'UNI'
        unit_code = int(self._query(cmd))
        return PRESSURE_UNITS[unit_code]

    def pressure_val_gauge1(self) -> float:
        """Returns pressure value of gauge one."""
        return self.pressure_gauge(1)[0]

    def pressure_val_gauge2(self) -> float:
        """Returns pressure value of gauge two."""
        return self.pressure_gauge(2)[0]

    def temperature(self) -> int:
        """Returns inner temperature of the Dual Gauge controller
        Unit is degrees celcius. Error is +-2 deg."""
        cmd = 'TMP'
        response = self._query(cmd)
        return int(response)

class TPG362Dummy:
    """For testing purpose. No devices needed."""
    def __init__(self, port=None):
        pass

    def initialize(self):
        pass

    def close(self):
        pass

    def idn(self):
        response = '-1'
        result = {
            'Type': response,
            'Model No.': response,
            'Serial No.': response,
            'Firmware version': response,
            'Hardware version': response,
        }
        return result

    def error_status(self):
        error = '0000'
        return error, ERRORS[error]

    def pressure_gauge(self, gauge: int):
        status_code = int(0)
        value = float(1)
        return value, (status_code, MEASUREMENT_STATUS[status_code])

    def pressure_gauges(self):
        return (self.pressure_gauge(1), self.pressure_gauge(2))

    def pressure_unit(self):
        return PRESSURE_UNITS[0]

    def pressure_val_gauge1(self) -> float:
        return self.pressure_gauge(1)

    def pressure_val_gauge2(self) -> float:
        return self.pressure_gauge(2)

    def temperature(self) -> int:
        return 20
