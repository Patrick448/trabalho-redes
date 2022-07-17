from socket import *
import os 
serverPort = 12000
clientName = 'localhost'
serverSocket = socket(AF_INET, SOCK_DGRAM)
#serverSocket.bind((clientName, serverPort))
#print ('The server is ready to receive')

segment_size = 1024
file = open("document.bin","rb")
file_stats = os.stat("document.bin").st_size
#content=file.read(file_stats)
print(file_stats)
#print (content)

cont =0


while cont <file_stats:
	file.seek(cont)
	content=file.read(segment_size)
	# print("\n----\n")
	# print(len(content))
	cont+=segment_size
	serverSocket.sendto(content, (clientName, serverPort))


file.close()
serverSocket.close()

# while True:
# 	print ('Waiting...')
# 	message, clientAddress = serverSocket.recvfrom(1024)
# 	modifiedMessage = message.decode().upper()
# 	print (modifiedMessage)
# 	serverSocket.sendto(modifiedMessage.encode(), clientAddress)
# 	print ('closing socket...')

# serverSocket.close()
