from socket import *
import os
from time import sleep
from package import MyPackage
import atexit

remotePort = 12001
localPort = 12000
clientName = 'localhost'
clientAddress = (clientName, localPort)
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((clientName, localPort))

content_size = 252
segment_size = 256
file = None
file_path = "document2.bin"
file_stats = os.stat(file_path).st_size

PACKAGE_STATUS_UNSENT = 0
PACKAGE_STATUS_SENT = 1
PACKAGE_STATUS_ACKED = 2
PACKAGE_STATUS_ACKED_DUP = 3
PACKAGE_STATUS_NULL = -1

seqNum = 0
bufferSize = 10
buffer = [None] * bufferSize
windowSize = 3
windowStart = 0
status_list = [PACKAGE_STATUS_NULL] * bufferSize


def get_first_not_acked(array):
    for i, item in enumerate(array):
        if item != PACKAGE_STATUS_ACKED and item != PACKAGE_STATUS_NULL:
            return i

    return -1


def move_and_fill(buffer, amount):
    count = 0
    while count < len(buffer):
        buffer[count] = buffer[count + amount]
        count += 1

    buffer_count = len(buffer) - amount
    while buffer_count < bufferSize:
        file.seek(seqNum)
        content = file.read(content_size)
        p = MyPackage()
        p.makePkg(content.decode(), seqNum)
        seqNum += content_size
        buffer.append(p)
        buffer_count += 1


def fill(buffer, status_list, length):
    global seqNum

    buffer_count = 0
    while buffer_count < length:
        file.seek(seqNum)
        content = file.read(content_size)
        index = int((seqNum / MyPackage.CONTENT_SIZE) % bufferSize)

        p = MyPackage()
        p.makePkg(content.decode(), seqNum)
        seqNum += content_size
        # buffer.append(p)
        buffer[index] = p
        status_list[index] = PACKAGE_STATUS_UNSENT

        print("Conteudo: " + p.content)
        buffer_count += 1

        if len(content) < content_size:
            print(
                "###################################################################################################################################")
            return buffer_count

    return buffer_count


def send_window(start, end, buffer, status_list):
    print(f"Enviando janela de {start} a {end}")
    for bufferItem in buffer[start:end]:
        if bufferItem is not None:
            index = int((bufferItem.seqNum / MyPackage.CONTENT_SIZE) % bufferSize)
            if status_list[index] == PACKAGE_STATUS_UNSENT:
                serverSocket.sendto(bufferItem.myEncode(), (clientName, remotePort))
                status_list[index] = PACKAGE_STATUS_SENT
                print("Enviou mensagem / num sequencia: " + str(bufferItem.seqNum))


def receive_next_package():
    message, client_address = serverSocket.recvfrom(segment_size)
    package = MyPackage()
    package.myDecode(message)
    package.printPackage()
    return package


def ack_package_move_window(package):
    global windowStart
    buffer[int(((package.seqNum - MyPackage.CONTENT_SIZE) / MyPackage.CONTENT_SIZE) % bufferSize)] = None
    print(buffer)
    windowStart = get_first_not_acked(buffer)


def send_end_package():
    end_package = MyPackage()
    end_package.makePkg("", -1)
    serverSocket.sendto(end_package.myEncode(), (clientName, remotePort))


def reset_buffer():
    global buffer, status_list, bufferSize
    buffer = [None] * bufferSize
    status_list = [-1] * bufferSize


# WAIT FOR CLIENT TO REQUEST FILE
def wait_for_connection():
    print("----- Waiting for connection -----")

    while True:
        message, client_address = serverSocket.recvfrom(segment_size)
        package = MyPackage()
        package.myDecode(message)
        print("Received")
        # package.printPackage()

        serverSocket.sendto(package.myEncode(), (clientName, remotePort))
        print("Sent confirmation")

        message, client_address = serverSocket.recvfrom(segment_size)
        package = MyPackage()
        package.myDecode(message)
        print("Received final confirmation: CONNECTION ESTABLISHED")

        package.printPackage()
        return client_address


def send_file():
    while seqNum < file_stats:
        global windowStart
        global buffer
        reset_buffer()
        packages_in_buffer = fill(buffer, status_list, bufferSize)
        windowStart = 0

        send_window(windowStart, windowStart + windowSize, buffer, status_list)
        while status_list[packages_in_buffer - 1] < PACKAGE_STATUS_ACKED:
            package = receive_next_package()
            package_index_in_buffer = int(((package.seqNum - MyPackage.CONTENT_SIZE) / MyPackage.CONTENT_SIZE)
                                          % bufferSize)

            if status_list[package_index_in_buffer] == PACKAGE_STATUS_ACKED:
                status_list[package_index_in_buffer] = PACKAGE_STATUS_ACKED_DUP
            elif status_list[package_index_in_buffer] == PACKAGE_STATUS_ACKED_DUP:
                print("ACK TRIPLO")
            else:
                status_list[package_index_in_buffer] = PACKAGE_STATUS_ACKED

            if package_index_in_buffer >= windowStart:
                windowStart = package_index_in_buffer + 1
                send_window(windowStart, windowStart + windowSize, buffer, status_list)

            sleep(0.01)

    send_end_package()
    print('\nCLOSING CONNECTION...')
    file.close()


def exit_handler():
    serverSocket.close()
    print("SERVER STOPPED")


atexit.register(exit_handler)

while True:
    try:
        reset_buffer()
        seqNum = 0
        windowStart = 0
        file = open(file_path, "rb")
        clientAddress = wait_for_connection()
    except Exception as e:
        print("CONNECTION COULD NOT BE ESTABLISHED")
        print(str(e))
        # serverSocket.close()
    else:
        send_file()
