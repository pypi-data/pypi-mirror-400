from py_rawports.transport import RawPort, Interface
from py_rawports.interfaces import FileIO
import threading

link = ('/tmp/rawports/rfile', '/tmp/rawports/wfile')

def demo0():
    rport = RawPort()
    wport = RawPort()
    try:
        rport.open(Interface.FileIO, link[0])
        wport.open(Interface.FileIO, link[1])
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
        port.open(Interface.FileIO, link)
        port.write(b'Little pigs, let me come in.')
        print(port.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        port.close()

def demo2():
    port = RawPort()
    try:
        port.open(FileIO.Comm().open(link))
        port.write(b'Here\'s Johnny!')
        print(port.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        port.close()

def main():
    demo0()
    demo1()
    demo2()

if __name__ == '__main__':
    main()
