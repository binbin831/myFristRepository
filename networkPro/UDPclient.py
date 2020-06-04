import socket


target_host = "127.0.0.1"
target_port = 80

#建立一个socket对象
client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

#发送数据
meg ="abcd"
client.sendto(meg.encode("utf-8"),(target_host,target_port))

#接收数据
data= client.recv(1024).decode("utf-8")
print(data)