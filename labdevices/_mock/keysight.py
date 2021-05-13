""" Provides a mock for the pyvisa package used in the keysight devices. """
from unittest.mock import Mock
import pathlib

DATA_DIR = pathlib.Path(__file__).parent / 'data'

# The commands that are used in the methods of the keysight
# devices and typical responses.
QUERY_COMMANDS = {
    "*IDN?":                "Keysight dummy",
    "FREQuency:GATE:TIME?": "0.1",
    "TRIGger:SOURce?":      "IMM",
    "FETCH?":               "300000.314776433",
    ":MEASure:VAVerage?":   "0.1",
    ":MEASure:VMAX?":       "0.1",
    ":MEASure:VPP?":        "0.1",
    ":WAVeform:PREamble?":  (
        "+0,+0,+64516,+1,+1.55000309E-005,-5.00000000E-001,"
        "+0,+1.60804000E-004,+0.0E+000,+128"
        ),

}

class PyvisaDummy(Mock):
    """ Mock class for the pyvisa package when using the
    Keysight devices as dummy. """

    @staticmethod
    def query(command: str):
        """
        Containes all the query commands used in the keysight
        drivers and returns a result with the pattern of the
        actual device.
        """
        if command in QUERY_COMMANDS:
            return QUERY_COMMANDS[command]
        if "MEASure:FREQuency?" in command:
            return "10"
        return Mock()

    @staticmethod
    def query_binary_values(command: str, datatype: str) -> list:
        """
        Contains the commands used when calling query_binary_values
        in the keysight device divers and returns a single entry list
        with a corresponding binary value.
        """
        if command == ":DISPlay:DATA? PNG, COLor":
            file_dir = DATA_DIR / 'keysight_oscilloscope_screenshot.png'
            with open(file_dir, "rb") as f:
                return [f.read()]
        if command == ":WAVeform:DATA?":
            file_dir = DATA_DIR / 'keysight_oscilloscope_trace_bin'
            with open(file_dir, "rb") as f:
                return [f.read()]
        return [Mock()]
