import socket

s = socket.socket()
host = socket.gethostname()
port = 3030
s.bind((host, port))

s.listen(5)
c = None

while True:
	if c is None:
		# Halts
		print ('[Esperando conexao...]')
		c, addr = s.accept()
		print ('O cliente conectou ->', addr)
	else:
		# Halts
		print ('[Esperando resposta...]')
		print (c.recv(1024).decode())
		q = input('Escreva msg para o cliente:')
		c.send(q.encode())
