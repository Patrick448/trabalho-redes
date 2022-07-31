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
buffer = []
while isWhileEnabled:
    print("\n-----------\n")
    message, clientAddress = clientSocket.recvfrom(segment_size)
    p=MyPackage()
    p.myDecode(message)
    if(p.seqNum < 0):
        isWhileEnabled = False
    # p.printPackage()
    sleep(1)
    ack = MyPackage()
    ack.makePkg("ACK", p.seqNum)
    clientSocket.sendto(ack.myEncode(), ("localhost", remotePort))
    print("ACK: " + str(p.seqNum+len(message)))


print ('\nFechando socket cliente UDP...')
clientSocket.close()