from __future__ import annotations
from enum import IntEnum
from typing import Union

if __name__ == '__main__':
    import sys
    from os.path import dirname
    sys.path.append(dirname(dirname(__file__))) # append './../../' to sys.path

from py_rawports.interfaces import Socket, USB, Serial, FileIO, FileDescriptor

class Interface(IntEnum):
    Socket  = 0
    USB     = 1
    Serial  = 2
    FileIO  = 3
    FileDescriptor = 4

class RawPort:
    __INTF = (Socket.Comm, USB.Comm, Serial.Comm, FileIO.Comm, FileDescriptor.Comm)
    def __init__(self):
        self.__comm:Union[Socket.Comm, USB.Comm, Serial.Comm, FileIO.Comm, FileDescriptor.Comm] = None
    
    def isclosed(self)->bool:
        return self.__comm is None or self.__comm.isclosed()
    
    def isopen(self)->bool:
        return not self.isclosed()
    
    def open(self, *args)->RawPort:
        if(isinstance(args[0], RawPort.__INTF)):
            self.__open_instance(*args)
        else:
            self.__new_interface(*args)
        return self
    
    def close(self)->bool:
        if(not self.isclosed()):
            self.__comm.close()
        return True
    
    def read(self, len:int, timeout:float = None)->bytes:
        return self.__comm.read(len, timeout)

    def write(self, data:bytes, timeout:float = None)->int:
        return self.__comm.write(data, timeout)
    
    # open a communication instance
    def __open_instance(self, instance:Union[Socket.Comm, USB.Comm, Serial.Comm, FileIO.Comm, FileDescriptor.Comm]):
        self.close()
        self.__comm = instance
    
    # create an interface using default parameters
    def __new_interface(self, type:Interface, connection:tuple):
        self.close()
        self.__comm = RawPort.__INTF[type]()
        self.__comm.open(connection)

def main():
    port = RawPort()
    try:
        port.open(Interface.Socket, ('127.0.0.1', 11451))
        # port.open(Interface.USB, (0x1F3A, 0x3B04))
        # port.open(Interface.Serial, (r'\\.\COM7', 115200, 8))
        # port.open(Interface.FileIO, ('/home/johnsmith/rfile', '/home/johnsmith/wfile'))
        # port.open(Interface.FileDescriptor, ('/home/johnsmith/rfile', '/home/johnsmith/wfile'))
        port.write(b'test message!')
        print(port.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        port.close()

if __name__ == '__main__':
    main()
