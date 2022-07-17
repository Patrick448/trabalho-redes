import socket

s = socket.socket()
host = '192.168.15.5'
port = 3030

s.connect((host, port))
print ('Conectado ao', host)

while True:
	z = input('Escreva algo para o servidor:')
	s.send(z.encode())
	# Halts
	print ('[Esperando resposta...]')
	print (s.recv(1024).decode())
