from __future__ import annotations
import os, sys
from typing import Tuple, Union

_PathPair = Tuple[str, str] # read_path write_path
_PathRW = str # rw_path

def _checkPathArgs(pth:Union[_PathPair, _PathRW])->Union[_PathPair, None]:
    __pthpair = None
    if(isinstance(pth, str)):
        __pthpair = (pth, pth)
    elif(isinstance(pth, (list, tuple)) and len(pth) == 2):
        if(isinstance(pth[0], str) and isinstance(pth[1], str)):
            __pthpair = (pth[0], pth[1])
    return __pthpair

class Comm:
    def __init__(self, rmode:int=os.O_RDONLY, wmode:int=os.O_WRONLY):
        self.__rmode:int = rmode
        self.__wmode:int = wmode
        if sys.platform == "win32":
            self.__rmode |= os.O_BINARY
            self.__wmode |= os.O_BINARY
        self.__fd_read:int = -1
        self.__fd_write:int = -1
    
    def isclosed(self)->bool:
        if(self.__fd_read == -1 or self.__fd_write == -1):
            return True
        return False

    def isopen(self)->bool:
        return not self.isclosed()
    
    # open fd_read fd_write
    def open(self, pth:Union[_PathPair, _PathRW])->Comm:
        self.close()
        __pthpair = _checkPathArgs(pth)
        if(__pthpair is None):
            raise IOError('pth must be pathstr or (pathstr, pathstr)')
        self.__fd_read = os.open(__pthpair[0], self.__rmode)
        self.__fd_write = os.open(__pthpair[1], self.__wmode)
        if(self.isclosed()):
            raise IOError('Can not open file descriptor! check file path')
        return self

    def close(self)->bool:
        if(not self.isclosed()):
            if(self.__fd_read != -1):
                try:
                    os.close(self.__fd_read)
                finally:
                    self.__fd_read = -1
            if(self.__fd_write != -1):
                try:
                    os.close(self.__fd_write)
                finally:
                    self.__fd_write = -1
        return True

    def read(self, len:int, timeout:float=None)->bytes:
        if(self.isclosed()):
            raise IOError('read file descriptor is close!')
        return os.read(self.__fd_read, len)

    def write(self, data:bytes, timeout:float=None)->int:
        if(self.isclosed()):
            raise IOError('write file descriptor is close!')
        return os.write(self.__fd_write, data)

def main():
    comm = Comm()
    try:
        comm.open(('/tmp/rawports/rfile', '/tmp/rawports/wfile'))
        comm.write(b'fd message!')
        print(comm.read(32))
    except Exception as e:
        print(f'Exception:{e} ')
    finally:
        comm.close()

if __name__ == '__main__':
    main()