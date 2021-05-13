""" Provides a mock for the pyvisa package used in the Rohde & Schwarz devices. """
from unittest.mock import Mock
import pathlib

DATA_DIR = pathlib.Path(__file__).parent / 'data'

# The commands that are used in the methods of the Rohde & Schwarz
# devices and typical responses.
QUERY_COMMANDS = {
    # Rohde & Schwarz device commands
    "*IDN?":                "Rohde&Schwarz dummy",
    "SYST:ERR:ALL?":        "0,'No error'\n",
    # Spectrum Analyzer commands
    "FREQ:STAR?":           "181000000.000000\n",
    "FREQ:STOP?":           "281000000.000000\n",
    # Oscilloscope commands
    "MEASurement:RESult?": "0.1",
}

class PyvisaDummy(Mock):
    """ Mock class for the pyvisa package when using the
    Rohde & Schwarz devices as dummy. """

    @staticmethod
    def query(command: str):
        """
        Containes all the query commands used in the Rohde & Schwarz
        drivers and returns a result with the pattern of the
        actual device.
        """
        if command in QUERY_COMMANDS:
            return QUERY_COMMANDS[command]
        if command == "TRACe:DATA? TRACE1":
            file_dir = DATA_DIR / 'rohde_schwarz_spectrum_analyzer_trace.txt'
            with open(file_dir, "r") as f:
                return f.read()
        if "FORMat ASC; CHANnel" in command:
            file_dir = DATA_DIR / 'rohde_schwarz_oscilloscope_trace.txt'
            with open(file_dir, "r") as f:
                return f.read()
        if ":DATA:HEADer?" in command:
            return "-3.00000E-08, 2.99500E-08, 1200, 1"
        return Mock()

    @staticmethod
    def query_binary_values(command: str, datatype: str) -> list:
        """
        Contains the commands used when calling query_binary_values
        in the rohde and schwarz device divers and returns a single entry list
        with a corresponding binary value.
        """
        if command == "HCOPy:DATA?":
            file_dir = DATA_DIR / 'rohde_schwarz_oscilloscope_screenshot.png'
            with open(file_dir, "rb") as f:
                return [f.read()]
        return [Mock()]
