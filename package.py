from importlib.resources import contents


class MyPackage:
    content = ""
    seqNum = 0
    encodedStringTeste = bytes

    def __init__(self):
        pass

    def makePkg(self, content, seqNum):
        self.content = content
        self.seqNum = seqNum

    def myEncode(self):
        encoded_seq_num = int(self.seqNum).to_bytes(4, "big", signed=True)
        enconded_content = str(self.content).encode()
        self.encodedStringTeste = encoded_seq_num + enconded_content
        return encoded_seq_num + enconded_content

    def myDecode(self, encoded_package):
        self.content = encoded_package[4:].decode()
        self.seqNum = int.from_bytes(encoded_package[:4], "big", signed=True)

    def printPackage(self):
        print("Numero de sequencia: " + str(self.seqNum))
        print("Conteudo: " + str(self.content))