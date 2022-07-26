from socket import *
from package import MyPackage

serverName = 'localhost'
remotePort = 12000
localPort = 12001
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind((serverName, localPort))



print ('Waiting...')
while True:
    print ('\n------------\n')
    message, clientAddress = clientSocket.recvfrom(1024)
    p=MyPackage()
    p.myDecode(message)
   # print(message)
   # clientSocket.sendto("teste pelo amor de deus funciona".encode(), ("localhost", remotePort))

print ('closing socket...')
clientSocket.close()