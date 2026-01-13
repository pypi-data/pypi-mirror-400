
from __future__ import annotations
import usb.core, usb.util, libusb_package
from usb.backend import libusb1
from usb.core import Device

from typing import Union, List, Tuple, Optional

be = libusb1.get_backend(find_library=libusb_package.find_library)

_HWID = Tuple[int, int, Optional[int]] # VID, PID, address

class _HWIDMatch:
    def __init__(self, hwID:_HWID):
        self.VID:int = int(hwID[0])
        self.PID:int = int(hwID[1])
        self.ADDR:Union[int, None] = None
        if(len(hwID) > 2):
            self.ADDR = int(hwID[2])
    
    def __call__(self, dev:Device)->bool:
        __MATCH_ADDR = self.ADDR is None or dev.address == self.ADDR
        return dev.idVendor == self.VID and dev.idProduct == self.PID and __MATCH_ADDR

class _DEVInfo:
    # usbdevice info, match one device via _HWIDMatch
    def __init__(self, match_func:_HWIDMatch, DEVNAME:str):
        self.__match_func:_HWIDMatch = match_func
        self.__devname:str = DEVNAME
    
    def __call__(self, dev:Device)->bool:
        return self.__match_func(dev)
    
    # return a tuple representing _HWID, which you can use to open the device using USB.Comm.open. 
    def HWID(self)->_HWID:
        return (self.__match_func.VID, self.__match_func.PID, self.__match_func.ADDR)
    
    # return to the device name configured in the product.
    def DevName(self)->str:
        return self.__devname

class _SCANInfo:
    # usbscan info, match HWID
    # if hwID.ADDR is None and host is connected to multiple devices with the same HWID, the scanner can scan all devices.
    # if hwID.ADDR is not None, then only one device will be matched.
    def __init__(self, hwID:_HWID):
        self.__match_func:_HWIDMatch = _HWIDMatch(hwID)
    
    def __call__(self, dev:Device)->bool:
        return self.__match_func(dev)

class _USBFinder:
    # _USBFinder.scan will try to scan all deivce that match _SCANInfo
    @classmethod
    def scan(cls, match_func:_SCANInfo)->Tuple[Device]:
        __devs_info:List[Device] = []
        if(callable(match_func)):
            for dev in usb.core.find(find_all=True, backend=be, custom_match=match_func):
                __devs_info.append(_DEVInfo(_HWIDMatch(dev.idVendor, dev.idProduct, dev.address), dev.product))
        return tuple(__devs_info)

    # _USBFinder.find will find only one device that matches _DEVInfo or _SCANInfo
    @classmethod
    def find(cls, match_func:Union[_DEVInfo, _SCANInfo])->Union[Device, None]:
        __dev = None
        if(callable(match_func)):
            __dev:Device = usb.core.find(find_all=False, backend=be, custom_match=match_func)
        return __dev

class Comm:
    def __init__(self, inEndpoint:int=0x81, outEndpoint:int=0x01):
        self.__INEP:int = inEndpoint
        self.__OUTEP:int = outEndpoint
        self.__dev:Device = None
    
    def isclosed(self)->bool:
        if(self.__dev is None):
            return True
        return False
    
    def isopen(self)->bool:
        return not self.isclosed()
    
    # open usb device by (VID, PID, addr(optional))
    def open(self, hwID:_HWID)->Comm:
        self.close()
        self.__dev = _USBFinder.find(_SCANInfo(hwID))
        if(self.isclosed()):
            raise IOError('Can not find a usb device!')
        return self
    
    def close(self)->bool:
        if(not self.isclosed()):
            usb.util.dispose_resources(self.__dev)
        self.__dev = None
        return True

    def read(self, len:int, timeout:float=None)->bytes:
        if(self.isclosed()):
            raise IOError('usb is close!')
        if(timeout is not None):
            timeout = int(timeout * 1000) # s -> ms
        data = self.__dev.read(self.__INEP, len, timeout)
        return data.tobytes()

    def write(self, data:bytes, timeout:float=None)->int:
        if(self.isclosed()):
            raise IOError('usb is close!')
        if(timeout is not None):
            timeout = int(timeout * 1000) # s -> ms
        return self.__dev.write(self.__OUTEP, data, timeout)

def main():
    comm = Comm()
    try:
        comm.open((0x1F3A, 0x3B04))
        comm.write(b'usb message!')
        print(comm.read(32))
    except Exception as e:
        print(f'Exception:{e} ')
    finally:
        comm.close()

if __name__ == '__main__':
    main()