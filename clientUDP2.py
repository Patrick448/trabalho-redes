from socket import socket, AF_INET, SOCK_DGRAM
from package import MyPackage
from time import sleep
import random
from datetime import datetime


serverName = 'localhost'
remotePort = 12000
localPort = 12001
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind((serverName, localPort))

segment_size = MyPackage.SEGMENT_SIZE
#print('Cliente aguardando...')

bufferSize = 100
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
            file.write(p.content.encode())

    file.close()


def get_first_gap(array):
    for i, item in enumerate(array):
        if item is None:
            return i

    return len(array)

def establish_connection():
    print("ESTABLISHING CONNECTION")
    package = MyPackage()
    package.makePkg("EST", windowSize)
    clientSocket.sendto(package.myEncode(), ("localhost", remotePort))
    print("sent connection request")

    while True:
        message, client_address = clientSocket.recvfrom(segment_size)
        package = MyPackage()
        package.myDecode(message)
        # package.printPackage()
        print("received confirmation")

        package = MyPackage()
        package.makePkg("EST", windowSize)  
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
    last_buffer_iteration_seq_num = 0

    while True:
        print("\n------------\n")
        message, client_address = clientSocket.recvfrom(segment_size)
        p = MyPackage()
        p.myDecode(message)

        if buffer_occupation == bufferSize or p.seqNum < 0:
            write_buffer_to_file(receivedFilePath, buffer)
            buffer = [None] * bufferSize
            buffer_occupation = 0
            windowStart = 0
            last_buffer_iteration_seq_num += nextSeqNum

        if p.seqNum < 0:
            break

        package_index_in_buffer = int((p.seqNum / MyPackage.CONTENT_SIZE)) % bufferSize
        random.seed(datetime.now().timestamp())

        if package_index_in_buffer >= windowStart and p.seqNum >= last_buffer_iteration_seq_num:
            random_discard = random.choices([False, True], [98, 2], k=1)
            print(random_discard)
            if random_discard[0] is False:
                if buffer[package_index_in_buffer] is None:
                    buffer[package_index_in_buffer] = p
                    print_list(windowStart, windowStart + windowSize, buffer)
                    buffer_occupation += 1
            else:
                print(f"discarded {p.seqNum}")
                continue

        #sleep(0.01)
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
            nextSeqNum = last_buffer_iteration_seq_num + windowStart*MyPackage.CONTENT_SIZE
            ack = MyPackage()
            ack.makePkg("ACK", nextSeqNum)
            clientSocket.sendto(ack.myEncode(), ("localhost", remotePort))
            print("ACK dup: " + str(nextSeqNum))
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
