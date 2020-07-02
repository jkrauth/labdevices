"""
Driver for devices from Stanford Research Systems
contains:
- DG645

File name: stanford_research_systems.py
Python version: 3.7
"""
import socket
import time


class DG645:

    DEFAULTS = {
        'outputBNC': {
            "T0":0,
            "AB":1,
            "CD":2,
            "EF":3,
            "GH":4
        },
        'channel': {
            "T0":0,
            "T1":1,
            "A":2,
            "B":3,
            "C":4,
            "D":5,
            "E":6,
            "F":7 ,
            "G":8,
            "H":9
        },
        'write_termination': '\n',
        'read_termination': '\r\n',
    }
    
    
    def __init__(self, tcp, port, timeout = 0.1):    
        self.tcp = tcp
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(timeout)

    def initialize(self):
        self.s.connect((self.tcp, self.port))
        #self.s.send(b'*IDN?\n')
        #self.idn = self.s.recv(256)
        print('Connected to delay generator 645 instance:\n', self.idn)

    def close(self):
        time.sleep(1)
        self.s.close()
        print("Close connection to:\n", self.idn)
  
    def write(self, cmd: str):
        # Add write termination character and encode
        termination_char = self.DEFAULTS['write_termination']
        cmd += termination_char
        cmd = cmd.encode()
        # Send command
        self.s.send(cmd)
        
    def query(self, cmd: str) -> str:
        self.write(cmd)
        respons = self.s.recv(256)
        respons = respons.decode()
        # Strip off read termination character
        return respons.rstrip()
        
    @property
    def idn(self):
        idn = self.query('*IDN?')
        return idn
    
    def setDelay(self, channel, delay, reference = "T0"):
        
        if isinstance(channel, str):
            channel = self.DEFAULTS['channel'][channel]
        
        if isinstance(reference, str):    
            reference = self.DEFAULTS['channel'][reference]

        cmd = f'DLAY {channel}, {reference}, {delay}'
        self.write(cmd)
        #wait for 100 ms, this is the time is will take to write the command
        time.sleep(100*0.001)
    
    def getDelay(self, channel) -> float:
        
        if isinstance(channel, str):
            channel = self.DEFAULTS['channel'][channel]
        cmd = f'DLAY? {channel}'
        respons = self.query(cmd)
        return float(respons[2:])
    
    def getOutputLevel(self, channel):
        
        if isinstance(channel, str):
            channel = self.DEFAULTS['outputBNC'][channel]
        cmd = f'LAMP? {channel}'
        respons = self.query(cmd)
        return answer


class DG645DUMMY:
    def __init__(self,  tcp, port, timeout = 0.1):
        pass

    def initialize(self):
        print('Connected to DUMMY delay generator 645')
        self.delay = 1
        self.outputlevel = 2

    def setDelay(self, channel, delay, reference = "T0"):
        self.delay = delay

    def getDelay(self, channel):
        return self.delay

    def getOutputLevel(self, channel):
        return self.outputlevel

# cutting = Delay_Generator_TCP('10.0.0.31', 5025)
# picking = Delay_Generator_TCP('10.0.0.30', 5025)


if __name__ == "__main__":
    dg = DG645('10.0.0.34', 5025)
    dg.initialize()
    respons = dg.getDelay(2)
    print(respons)
    dg.setDelay(2, 0.004061726)
    respons = dg.getDelay(2)
    print(respons)
    dg.close()
    
