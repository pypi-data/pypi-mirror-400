from __future__ import annotations
import socket
from typing import Union, Tuple

_Address = Tuple[str, int] # ip, port

class _AddressChecker:
    # check the ip address format and return the address family(or error message).
    @classmethod
    def __checkIpAddr(cls, ip_str:str):
        try:
            socket.inet_pton(socket.AF_INET, ip_str)
            return True, socket.AF_INET
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip_str)
                return True, socket.AF_INET6
            except socket.error:
                return False, 'Invalid IpAddress'

    # check the ip port and return the port number(or error message).
    @classmethod
    def __checkIpPort(cls, port:Union[int, str]):
        try:
            port_num = int(port)
            if(0 <= port_num <= 65535):
                return True, port_num
            else:
                return False, 'Port out of range(0-65535)'
        except ValueError:
            return False, 'Port must be number'
        except TypeError:
            return False, 'Port can not be None'
    
    # check (ip, port) and return the address family and (ip, port).
    @classmethod
    def check(cls, address:_Address)->bool:
        if(isinstance(address, (list, tuple))):
            if(len(address) == 2):
                status, addressfamily = cls.__checkIpAddr(address[0])
                if(status):
                    status, port_num = cls.__checkIpPort(address[1])
                    if(status):
                        return True, addressfamily, (address[0], port_num)
                    else:
                        error = port_num
                else:
                    error = addressfamily
        return False, error, None

class Comm:
    def __init__(self, SocketKind:socket.SocketKind=socket.SOCK_STREAM):
        self.__SocketKind:socket.SocketKind = SocketKind
        self.__socket:socket.socket = None
    
    # open a socket connection by (ip, port)
    def open(self, address:_Address)->Comm:
        self.close()
        status, __AddressFamily, address = _AddressChecker.check(address)
        if(status):
            self.__socket = socket.socket(__AddressFamily, self.__SocketKind)
            self.__socket.connect(address)
        else:
            raise IOError(__AddressFamily)
        return self
    
    def isclosed(self)->bool:
        if(self.__socket is None):
            return True
        return False
    
    def isopen(self)->bool:
        return not self.isclosed()
    
    def close(self)->bool:
        if(not self.isclosed()):
            self.__socket.close()
        self.__socket = None
        return True
    
    def read(self, len:int, timeout:float=None)->bytes:
        if(self.isclosed()):
            raise IOError('socket is close!')
        self.__socket.settimeout(timeout)
        return self.__socket.recv(len)
    
    def write(self, data:bytes, timeout:float=None)->int:
        if(self.isclosed()):
            raise IOError('socket is close!')
        self.__socket.settimeout(timeout)
        return self.__socket.send(data)

def main():
    comm = Comm()
    try:
        comm.open(('127.0.0.1', 11451))
        comm.write(b'socket message!')
        print(comm.read(32))
    except Exception as e:
        print(f'Exception:{e} ')
    finally:
        comm.close()

if __name__ == '__main__':
    main()