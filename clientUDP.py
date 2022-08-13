from importlib.resources import Package
from socket import *
from package import MyPackage
from time import sleep 

serverName = 'localhost'
remotePort = 12000
localPort = 12001
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind((serverName, localPort))

segment_size = 256
print ('Cliente aguardando...')
isWhileEnabled = True

bufferSize = 20
buffer = [None] * bufferSize
windowSize = 10
windowStart = 0
nextSeqNum =0
receivedFilePath = "received.bin"

def writeBufferToFile(filePath, buffer):

    file = open(filePath,"wb+")
    for p in buffer:
        print(p)
        if p != None:
            file.write("\n------\n".encode() + str(p.seqNum).encode() +p.content.encode())
        
    file.close()

def getFirstGap(array):
    for i, item in enumerate(array):
        if item == None:
            return i

while isWhileEnabled: 
    print("\n------------\n")
    message, clientAddress = clientSocket.recvfrom(segment_size)
    p=MyPackage()
    p.myDecode(message)
    if(p.seqNum < 0):
        isWhileEnabled = False
        break
        
    # p.printPackage()

    buffer[int((p.seqNum/MyPackage.CONTENT_SIZE)%bufferSize)] = p
    
    sleep(0.5)
    if(p.seqNum==nextSeqNum):
        ack = MyPackage()
        ack.makePkg("ACK", p.seqNum+MyPackage.CONTENT_SIZE)
        clientSocket.sendto(ack.myEncode(), ("localhost", remotePort))
        print("ACK: " + str(p.seqNum+len(message)+1))
        print(p.content)
        nextSeqNum = p.seqNum + MyPackage.CONTENT_SIZE
        windowStart+=1

    windowStart = (getFirstGap(buffer))%10

writeBufferToFile(receivedFilePath, buffer)
print ('\nFechando socket cliente UDP...')
clientSocket.close()

