from py_rawports.transport import RawPort, Interface
from py_rawports.interfaces import Socket

link = ('127.0.0.1', 11451)

def demo1():
    port = RawPort()
    try:
        port.open(Interface.Socket, link)
        port.write(b'Little pigs, let me come in.')
        print(port.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        port.close()

def demo2():
    port = RawPort()
    try:
        port.open(Socket.Comm().open(link))
        port.write(b'Here\'s Johnny!')
        print(port.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        port.close()

def main():
    demo1()
    demo2()

if __name__ == '__main__':
    main()
