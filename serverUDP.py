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
file = open("document.bin","rb")
file_stats = os.stat("document.bin").st_size

seqNum = 0
buffer=[]
bufferLength=5

def moveAndFill(buffer, amount):
	count = 0
	while count < len(buffer):
		buffer[count] = buffer[count + amount]
		count+=1
	
	bufferCount = len(buffer) - amount
	while bufferCount < bufferLength:
		file.seek(seqNum)
		content=file.read(content_size)
		p = MyPackage()
		p.makePkg(content.decode(), seqNum)
		seqNum += segment_size
		buffer.append(p)
		bufferCount+=1

def fill(buffer, length):
	global seqNum

	bufferCount = 0
	while bufferCount < length:
		file.seek(seqNum)
		content=file.read(content_size)
		p = MyPackage()
		p.makePkg(content.decode(), seqNum)
		seqNum += segment_size
		buffer.append(p)
		bufferCount+=1

while seqNum < file_stats:
	bufferCount = 0
	#1. popular o buffer
	# while bufferCount < bufferLength:
	# 	file.seek(seqNum)
	# 	content=file.read(content_size)
	# 	p = MyPackage()
	# 	p.makePkg(content.decode(), seqNum)
	# 	seqNum += segment_size
	# 	buffer.append(p)
	# 	bufferCount+=1

	buffer.clear()
	fill(buffer, bufferLength)

	#2. enviar todos pacotes do buffer
	for bufferItem in buffer:
		serverSocket.sendto(bufferItem.myEncode(), (clientName, remotePort))
		print("Enviou mensagem / num sequencia: " + str(bufferItem.seqNum))
		
	#3. esperar ACKs
	countAcks=0
	print("entrou no loop do servidor de esperar a resposta do cliente")
	while countAcks < bufferLength:
		message, clientAddress = serverSocket.recvfrom(segment_size)
		countAcks+=1
		ackPackage = MyPackage()
		ackPackage.myDecode(message)
		ackPackage.printPackage()

	sleep(1)

endPackage = MyPackage()
endPackage.makePkg("", -1)
serverSocket.sendto(endPackage.myEncode(), (clientName, remotePort))
print ('\nFechando socket servidor UDP...')
file.close()
serverSocket.close()



