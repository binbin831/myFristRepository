import socket


target_host = "192.168.13.150"
target_port = 9081

#建立一个socket对象
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#连接客户端
client.connect((target_host,target_port))
#发送一些数据
meg = input("请输入数据：")
client.send(meg.encode("utf-8"))
#接收一些数据
response = client.recv(4096)
print(response.decode('utf-8'))
client.close()

