from functools import partial
from socket import *
import os
from threading import Timer
from time import sleep
from package import MyPackage
import atexit

remote_port = 12001
local_port = 12000
clientName = 'localhost'
clientAddress = (clientName, remote_port)
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", local_port))

content_size = MyPackage.CONTENT_SIZE
segment_size = MyPackage.SEGMENT_SIZE
file = None
file_path = "arquivo_teste.txt"
file_stats = os.stat(file_path).st_size

PACKAGE_STATUS_UNSENT = 0
PACKAGE_STATUS_SENT = 1
PACKAGE_STATUS_ACKED = 2
PACKAGE_STATUS_ACKED_DUP = 3
PACKAGE_STATUS_NULL = -1

clientWindowSize = None
seqNum = 0
bufferSize = 100
buffer = [None] * bufferSize
windowSize = 3
status_list = [PACKAGE_STATUS_NULL] * bufferSize


def get_first_not_acked(array):
    for i, item in enumerate(array):
        if item != PACKAGE_STATUS_ACKED and item != PACKAGE_STATUS_NULL:
            return i

    return -1


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

        #print("Conteudo: " + p.content)
        buffer_count += 1

        if len(content) < content_size:
            return buffer_count

    return buffer_count


def send_window(start, end, buffer, status_list, resend):
    print(f"Enviando janela de {start} a {end}")
    for bufferItem in buffer[start:end]:
        if bufferItem is not None:
            index = int((bufferItem.seqNum / MyPackage.CONTENT_SIZE) % bufferSize)
            if status_list[index] == PACKAGE_STATUS_UNSENT or resend:
                serverSocket.sendto(bufferItem.myEncode(), clientAddress)
                status_list[index] = PACKAGE_STATUS_SENT
                print("Enviou mensagem / num sequencia: " + str(bufferItem.seqNum))


def receive_next_package():
    message, client_address = serverSocket.recvfrom(segment_size)
    package = MyPackage()
    package.myDecode(message)
    #package.printPackage()
    return package


def send_end_package():
    end_package = MyPackage()
    end_package.makePkg("", -1)
    serverSocket.sendto(end_package.myEncode(), clientAddress)


def reset_buffer():
    global buffer, status_list, bufferSize
    buffer = [None] * bufferSize
    status_list = [-1] * bufferSize


# WAIT FOR CLIENT TO REQUEST FILE
def wait_for_connection():
    global clientWindowSize
    print("----- Waiting for connection -----")

    while True:
        message, client_address = serverSocket.recvfrom(segment_size)
        package = MyPackage()
        package.myDecode(message)
        clientWindowSize = package.seqNum
        print("Received")
        # package.printPackage()

        serverSocket.sendto(package.myEncode(), clientAddress)
        print("Sent confirmation")

        message, client_address = serverSocket.recvfrom(segment_size)
        package = MyPackage()
        package.myDecode(message)
        print("Received final confirmation: CONNECTION ESTABLISHED")

        #package.printPackage()
        return client_address


def send_file():
    t = None
    while seqNum < file_stats:
        global buffer
        reset_buffer()
        packages_in_buffer = fill(buffer, status_list, bufferSize)
        window_start = 0
        g = partial(send_window, 0, clientWindowSize, buffer, status_list, True)
        t = Timer(0.001, g)
        t.start()

        send_window(window_start, window_start + clientWindowSize, buffer, status_list, False)
        while status_list[packages_in_buffer - 1] < PACKAGE_STATUS_ACKED:

            package = receive_next_package()
            package_index_in_buffer = int(((package.seqNum - MyPackage.CONTENT_SIZE) / MyPackage.CONTENT_SIZE)
                                          % bufferSize)

            # ATUALIZA STATUS DOS PACOTES
            if status_list[package_index_in_buffer] == PACKAGE_STATUS_ACKED:
                status_list[package_index_in_buffer] = PACKAGE_STATUS_ACKED_DUP
            elif status_list[package_index_in_buffer] == PACKAGE_STATUS_ACKED_DUP:
                send_window(window_start, window_start + clientWindowSize, buffer, status_list, True)
            else:
                status_list[package_index_in_buffer] = PACKAGE_STATUS_ACKED

            # MOVE JANELA PARA DEPOIS DO INDICE DO ULTIMO PACOTE CONFIRMADO
            if package_index_in_buffer >= window_start:
                window_start = package_index_in_buffer + 1
                send_window(window_start, window_start + clientWindowSize, buffer, status_list, False)
                t.cancel()
                g = partial(send_window, window_start, window_start + clientWindowSize, buffer, status_list, True)
                t = Timer(0.001, g)
                t.start()

            #sleep(0.01)

    t.cancel()
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
        file = open(file_path, "rb")
        clientAddress = wait_for_connection()
    except Exception as e:
        print("CONNECTION COULD NOT BE ESTABLISHED")
        print(str(e))
        # serverSocket.close()
    else:
        send_file()

