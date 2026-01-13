from __future__ import annotations
from serial import Serial, serialutil
from typing import Tuple

_Serial = Tuple[str, int, int] # serial port, baudrate, bytesize

# in Macos/Linux, port_str is like /dev/tty.usbmodem12345678901, /dev/ttyGS0, /dev/ttyACM0
# in Windows, port_str is like \\.\COM3, COM4

class Comm:
    def __init__(self, parity:str=serialutil.PARITY_NONE, stopbits:int=serialutil.STOPBITS_ONE):
        self.__parity:str = parity
        self.__stopbits:int = stopbits
        self.__com:Serial = None
    
    def isclosed(self)->bool:
        if(self.__com is None):
            return True
        return False
    
    def isopen(self)->bool:
        return not self.isclosed()
    
    # open serial com by (serial port, baudrate, len)
    def open(self, serial:_Serial)->Comm:
        self.close()
        self.__com = Serial(port=serial[0], baudrate=serial[1], bytesize=serial[2], 
                               parity=self.__parity, stopbits=self.__stopbits
                               )
        if(self.isclosed()):
            raise IOError('Can not open a serial com!')
        return self

    def close(self)->bool:
        if(not self.isclosed()):
            self.__com.close()
        self.__com = None
        return True

    def read(self, len:int, timeout:float=None)->bytes:
        if(self.isclosed()):
            raise IOError('serial port is close!')
        self.__com.timeout = timeout
        return self.__com.read(len)

    def write(self, data:bytes, timeout:float=None)->int:
        if(self.isclosed()):
            raise IOError('serial port is close!')
        self.__com.write_timeout = timeout
        return self.__com.write(data)

def main():
    comm = Comm()
    try:
        comm.open(('/dev/tty.usbmodem12345678901', 115200, 8))
        comm.write(b'serial message!')
        print(comm.read(32))
    except Exception as e:
        print(f'Exception:{e} ')
    finally:
        comm.close()

if __name__ == '__main__':
    main()