from py_rawports.transport import RawPort, Interface
from py_rawports.interfaces import Serial

link = (r'\\.\COM7', 115200, 8)

def demo1():
    port = RawPort()
    try:
        port.open(Interface.Serial, link)
        port.write(b'Little pigs, let me come in.')
        print(port.read(32))
    except Exception as e:
        print(f'{e}')
    finally:
        port.close()

def demo2():
    port = RawPort()
    try:
        port.open(Serial.Comm().open(link))
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
