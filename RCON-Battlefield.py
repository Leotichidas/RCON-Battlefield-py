from struct import *
import binascii
import socket
import sys
import hashlib

def md5(salt, message):
    m = hashlib.new('md5')
    m.update(salt)
    m.update(bytes(message, "UTF-8"))
    return m.hexdigest()

def encodePacket(seq, words):
    header = pack('<H', 1) + pack('<H', seq)
    
    wordsCount = len(words)
    wordsLenght = 0
    for str in words:
        wordsLenght += len(str)

    size = pack('<I', 4 + 4 + 4 + 4 * wordsCount + wordsLenght + wordsCount)

    count = pack('<I', wordsCount)

    args = bytearray()
    for arg in words:
        args += pack('<I', len(arg))
        args += bytes(arg, "UTF-8")
        args.append(0x0)    

    return header + size + count + args

def decodePacket(data):
    argsCount = unpack_from('<I', data[8:12])[0]
    position = 12
    words = []

    while argsCount != 0:
        argsCount -= 1
        argLenght = unpack_from('<I', data[position:position+4])[0]
        position += 4;
        words.append((data[position:position+argLenght]).decode("UTF-8"))
        position = position + argLenght + 1

    return words

def main():
    #Variable
    sequence = 0
    
    #Main
    print("********** Battlefield RCON Server Manager - By Leotichidas ***********")
    ip = input("Enter ip of server: ")
    port = None;
    
    try:
        port = int(input("Enter port of server: "))
    except:
        port = None
    
    while port == None:
        try:
            port = int(input("Insert a number, please: "))
        except:
            port = None
            
    print()
    print("Contatting server " + ip + ":" + str(port) + "...")
    
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:    
        tcp.connect((ip, port))
    except:
        print("#Error during contatting the server specified.")
        print()
        input("Press a key to exit...")
        sys.exit(0)

    print("OK Connection established! Type login for authentication.")

    command = None

    while True:
        if command == None:
            print()
            command = input(">> ").split(" ")

        if command == ["quit"]:
            break
        elif command == ["login"]:
            command = ["login.hashed"]
        
        tcp.send(encodePacket(sequence, command))
        sequence += 1
        
        data = tcp.recv(16384)
        decodedData = decodePacket(data)

        print(" ".join(decodedData))

        if command == ["login.hashed"]:
            salt = binascii.unhexlify(decodedData[1])
            password = input("Enter RCON password: ")
            hashHex = str(md5(salt, password).upper())
            command = ["login.hashed", hashHex]
        else:
            command = None
    
    tcp.close()
    print()
    input("Press a key to exit...")
    
if __name__ == "__main__":
    main()


