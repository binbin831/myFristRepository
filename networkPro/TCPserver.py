import socket
import threading

bindIP = "192.168.13.150"
bindPort =9081

server =socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind((bindIP,bindPort))

server.listen(5)
print("[*]Listen on %s:%d"%(bindIP,bindPort))

#客户处理线程

def handleClient(clientSocket):
    request = clientSocket.recv(1024).decode("utf-8")
    print("[*] Received: %s"%request)

    #返还数据包
    msg = "ACK!"
    clientSocket.send(msg.encode('utf-8'))
    clientSocket.close()


while True:
    client,addr = server.accept()
    print("[*] Accept connection from: %s:%d"%(addr[0],addr[1]))
    clientHandler = threading.Thread(target=handleClient,args=(client,))
    clientHandler.start()
