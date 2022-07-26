from socket import *
import os 
from package import MyPackage

remotePort = 12001
localPort = 12000
clientName = 'localhost'
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind((clientName, localPort))
#print ('The server is ready to receive')

segment_size = 1020
file = open("document.bin","rb")
file_stats = os.stat("document.bin").st_size
#content=file.read(file_stats)
print(file_stats)


#p = MyPackage("doce de leite de coimbra é o 2o melhor do brasil :)", 123456789)
#p.decode()

seqNum = 0
while seqNum < file_stats:
	file.seek(seqNum)
	content=file.read(segment_size)
	seqNum += segment_size
	p = MyPackage()
	p.makePkg(content.decode(), seqNum)
	serverSocket.sendto(p.myEncode(), (clientName, remotePort))
	#message, clientAddress = serverSocket.recvfrom(1024)
	#print (message.decode())

file.close()
serverSocket.close()


