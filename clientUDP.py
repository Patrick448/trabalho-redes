from socket import *

serverName = 'localhost'
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind((serverName, serverPort))
#message = input('Input lowercase sentence:')
#clientSocket.sendto(message.encode(), (serverName, serverPort))
#modifiedMessage, serverAddress = clientSocket.recvfrom(1024)
#print (modifiedMessage.decode())

print ('Waiting...')
while True:
    print ('\n------------\n')
    message, clientAddress = clientSocket.recvfrom(1024)
    print (message.decode())
    #clientSocket.sendto(modifiedMessage.encode(), clientAddress)

print ('closing socket...')
clientSocket.close()