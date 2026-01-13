from py_rawports.transport import RawPort, Interface
from py_rawports.interfaces import FileDescriptor
import threading, os

link = ('/tmp/rawports/rfile', '/tmp/rawports/wfile')

def demo0():
    rport = RawPort()
    wport = RawPort()
    try:
        rport.open(Interface.FileDescriptor, link[0])
        wport.open(Interface.FileDescriptor, link[1])
        rport.write(b'Little pigs, let me come in.')
        wport.write(b'Little pigs, let me come out.')
        print(rport.read(32))
        print(wport.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        rport.close()


def demo1():
    port = RawPort()
    try:
        port.open(Interface.FileDescriptor, link)
        port.write(b'Little pigs, let me come in.')
        print(port.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        port.close()

def demo2():
    port = RawPort()
    try:
        port.open(FileDescriptor.Comm().open(link))
        port.write(b'Here\'s Johnny!')
        print(port.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        port.close()

def demo3():
    def AtoB():
        print('A write to B start')
        link = ('/tmp/rawports/pipe-b-a', '/tmp/rawports/pipe-a-b')
        port = RawPort()
        try:
            port.open(FileDescriptor.Comm(os.O_RDWR, os.O_RDWR).open(link))
            port.write(b'Little pigs, let me come in.')
            print(port.read(32))
        except Exception as e:
            print(f'{e}')
        finally:
            port.close()

    def BtoA():
        print('B write to A start')
        link = ('/tmp/rawports/pipe-a-b', '/tmp/rawports/pipe-b-a')
        port = RawPort()
        try:
            port.open(FileDescriptor.Comm(os.O_RDWR, os.O_RDWR).open(link))
            print(port.read(32))
            port.write(b'Little pigs, let me come out.')
        except Exception as e:
            print(f'{e}')
        finally:
            port.close()
    
    threading.Thread(target=AtoB).start()
    threading.Thread(target=BtoA).start()

def main():
    demo0()
    demo1()
    demo2()
    demo3()

if __name__ == '__main__':
    main()
