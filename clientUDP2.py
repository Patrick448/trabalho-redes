from socket import *
from package import MyPackage
from time import sleep

serverName = 'localhost'
remotePort = 12000
localPort = 12001
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind((serverName, localPort))

segment_size = 256
print('Cliente aguardando...')

bufferSize = 5
buffer = [None] * bufferSize
windowSize = 10
windowStart = 0
nextSeqNum = 0
receivedFilePath = "received.bin"


def print_list(start, end, list):
    print("PRINT WINDOW")
    for i, item in enumerate(list[start:end]):
        print(f'{start + i}: {item}')


def create_file(file_path):
    file = open(file_path, "wb+")
    file.close()


def write_buffer_to_file(file_path, buffer):
    print("\nWRITING BUFFER TO FILE")
    file = open(file_path, "ab")
    for p in buffer:
        print(p)
        if p is not None:
            file.write("\n------\n".encode() + str(p.seqNum).encode() + p.content.encode())

    file.close()


def get_first_gap(array):
    for i, item in enumerate(array):
        if item is None:
            return i


def establish_connection():
    print("ESTABLISHING CONNECTION")
    package = MyPackage()
    package.makePkg("EST", 0)
    clientSocket.sendto(package.myEncode(), ("localhost", remotePort))
    print("sent connection request")

    while True:
        message, client_address = clientSocket.recvfrom(segment_size)
        package = MyPackage()
        package.myDecode(message)
        # package.printPackage()
        print("received confirmation")

        package = MyPackage()
        package.makePkg("EST", 0)
        clientSocket.sendto(package.myEncode(), ("localhost", remotePort))
        print("sent final confirmation: CONNECTION ESTABLISHED")
        return


def main_loop():
    global windowStart
    global seqNum
    global nextSeqNum
    global buffer
    is_while_enabled = True
    buffer_occupation = 0
    create_file(receivedFilePath)

    while is_while_enabled:
        print("\n------------\n")
        message, client_address = clientSocket.recvfrom(segment_size)
        p = MyPackage()
        p.myDecode(message)

        if buffer_occupation == bufferSize or p.seqNum < 0:
            write_buffer_to_file(receivedFilePath, buffer)
            buffer = [None] * bufferSize
            buffer_occupation = 0

        if p.seqNum < 0:
            is_while_enabled = False
            break
        # p.printPackage()

        buffer[int((p.seqNum / MyPackage.CONTENT_SIZE)) % bufferSize] = p
        print_list(windowStart, windowStart + 10, buffer)
        buffer_occupation += 1
        sleep(0.01)
        # SE RECEBIDO EM ORDEM
        if p.seqNum == nextSeqNum:
            ack = MyPackage()
            ack.makePkg("ACK", p.seqNum + MyPackage.CONTENT_SIZE)
            clientSocket.sendto(ack.myEncode(), ("localhost", remotePort))
            print("ACK: " + str(p.seqNum + len(message) + 1))
            print(p.content)
            nextSeqNum = p.seqNum + MyPackage.CONTENT_SIZE
            windowStart += 1
        # FORA DE ORDEM
        else:
            windowStart = get_first_gap(buffer)
            ack = MyPackage()
            ack.makePkg("ACK", nextSeqNum)
            clientSocket.sendto(ack.myEncode(), ("localhost", remotePort))
            print("ACK dup: " + nextSeqNum)
            print(p.content)

    print('\nFechando socket cliente UDP...')
    clientSocket.close()


try:
    establish_connection()
except Exception as e:
    print("CONNECTION COULD NOT BE ESTABLISHED")
    clientSocket.close()
else:
    main_loop()
