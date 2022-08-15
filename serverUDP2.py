from socket import *
import os
from time import sleep
from package import MyPackage

remotePort = 12001
localPort = 12000
clientName = 'localhost'
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((clientName, localPort))

content_size = 252
segment_size = 256
file = open("document.bin", "rb")
file_stats = os.stat("document.bin").st_size

PACKAGE_STATUS_UNSENT = 0
PACKAGE_STATUS_SENT = 1
PACKAGE_STATUS_ACKED = 2
PACKAGE_STATUS_NULL = -1

seqNum = 0
bufferSize = 10
buffer = [None] * bufferSize
windowSize = 3
windowStart = 0
ackList = [0] * windowSize
statusList = [PACKAGE_STATUS_NULL] * bufferSize


def getFirstNotAcked(array):
    for i, item in enumerate(array):
        if item != PACKAGE_STATUS_ACKED and item != PACKAGE_STATUS_NULL:
            return i

    return -1

def moveAndFill(buffer, amount):
    count = 0
    while count < len(buffer):
        buffer[count] = buffer[count + amount]
        count += 1

    bufferCount = len(buffer) - amount
    while bufferCount < bufferSize:
        file.seek(seqNum)
        content = file.read(content_size)
        p = MyPackage()
        p.makePkg(content.decode(), seqNum)
        seqNum += content_size
        buffer.append(p)
        bufferCount += 1


def fill(buffer, statusList, length):
    global seqNum

    bufferCount = 0
    while bufferCount < length:
        file.seek(seqNum)
        content = file.read(content_size)
        index = int(((seqNum) / MyPackage.CONTENT_SIZE) % bufferSize)

        p = MyPackage()
        p.makePkg(content.decode(), seqNum)
        seqNum += content_size
        #buffer.append(p)
        buffer[index] = p
        statusList[index] = PACKAGE_STATUS_UNSENT

        print("Conteudo: " + p.content)
        bufferCount += 1

        if len(content) < content_size:
            print(
                "###################################################################################################################################")
            break




def sendWindow(start, end, buffer, statusList):
    print(f"Enviando janela de {start} a {end}")
    for bufferItem in buffer[start:end]:
        if bufferItem is not None:
            index = int(((bufferItem.seqNum) / MyPackage.CONTENT_SIZE) % bufferSize)
            if statusList[index] == PACKAGE_STATUS_UNSENT:
                serverSocket.sendto(bufferItem.myEncode(), (clientName, remotePort))
                statusList[index] = PACKAGE_STATUS_SENT
                print("Enviou mensagem / num sequencia: " + str(bufferItem.seqNum))

def receiveNextPackage():
    message, clientAddress = serverSocket.recvfrom(segment_size)
    package = MyPackage()
    package.myDecode(message)
    package.printPackage()
    return package

def ackPackageMoveWindow(package):
    global windowStart
    buffer[int(((package.seqNum - MyPackage.CONTENT_SIZE) / MyPackage.CONTENT_SIZE) % bufferSize)] = None
    print(buffer)
    windowStart = getFirstNotAcked(buffer)


def sendEndPackage():
    endPackage = MyPackage()
    endPackage.makePkg("", -1)
    serverSocket.sendto(endPackage.myEncode(), (clientName, remotePort))

def reset_buffer():
    global buffer, statusList, bufferSize
    buffer = [None] * bufferSize
    statusList = [-1] * bufferSize

def main_loop():
    while seqNum < file_stats:
        global windowStart
        global buffer
        reset_buffer()
        fill(buffer, statusList, bufferSize)
        windowStart = 0

        while windowStart != -1:
            # todo: sendWindow will send repeated packages, fix it
            # maybe use a vector with the status of all packages (unsent, sent, acked)

            sendWindow(windowStart, windowStart + windowSize, buffer, statusList)
            while buffer[windowStart] is not None:
                package = receiveNextPackage()
                packageIndexInBuffer = int(((package.seqNum - MyPackage.CONTENT_SIZE) / MyPackage.CONTENT_SIZE)
                                           % bufferSize)
                #buffer[packageIndexInBuffer] = None
                statusList[packageIndexInBuffer] = PACKAGE_STATUS_ACKED

            windowStart = getFirstNotAcked(statusList)
            sleep(0.5)

    sendEndPackage()
    print('\nFechando socket servidor UDP...')
    file.close()
    serverSocket.close()


main_loop()
