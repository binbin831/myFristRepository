import socket
import os
import struct
from ctypes import *
import threading
import time
from netaddr import IPNetwork, IPAddress
import logging

logging.basicConfig(level=logging.WARNING)
# host to listen on
host = "192.168.43.144"

# 目标网段
subnet = "192.168.43.0/24"

# 自定义字段，用于辨别收到的包是否是响应我们的UDP请求。
magic_message = b"oddboy will be a great hacker"


# 批量发送UDP数据包
def udp_sender(subnet, magic_message):
    time.sleep(2)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.info("upd_sender,开始遍历IP")
    for ip in IPNetwork(subnet):  # 未能进入for循环。。。
        try:
            sender.sendto(magic_message, ("%s" % ip, 65212))
            logging.info("Scanning %s ..." % ip)
            # 这个端口应该是可以设定为大于1023的任意不常用端口。
        except Exception as e:
            logging.debug(e)
    logging.info("upd_sender,遍历结束。")


# IP包头定义
class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint),
        ("dst", c_uint)
    ]

    def __new__(cls, socket_buffer=None):  # 这里的cls与self作用相同，都是指代类本身。
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        # map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
        # inet_ntoa() -- 将32bit数值转换为IP地址
        # '<' 表示Little-endtion(小端) ? 为什么用小端呢？ 网络序不都是大端吗？
        # L   unsigned loog

        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


# ICMP（Internet Control Message Protocol）包头
class ICMP(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort),
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass


# create a raw socket and bind it to the public interface
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# we want the IP headers included in the capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# if we're using Windows, we need to send an IOCTL to set up promiscuous mode
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# 开始发送UDP包
t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
t.start()
logging.info("开始网段扫描...")

try:
    while True:
        # read in a packet
        logging.info("Recving...")
        raw_buffer = sniffer.recvfrom(65565)[0]

        # create an IP header from the first 20 bytes of the buffer
        ip_header = IP(raw_buffer[0:20])

        # print out the protocol that was detected and the hosts
        # print ("Protocol: %s %s -> %s" % (ip_header.protocol,
        #                                 ip_header.src_address,
        #                                 ip_header.dst_address))
        # 如果为ICMP，则进一步处理。
        if ip_header.protocol == "ICMP":
            # 计算ICMP包的起始位置（因为IP包头的长度是20-60字节不等，所以需要通过IP包头中信息来判断IP包头的真实长度）
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            # 解构ICMP数据
            icmp_header = ICMP(buf)

            logging.debug("\t\t\t\t\t\tICMP -> Type: %d Code: %d" % (icmp_header.type, icmp_header.code))

            # 收到检查类型为3，代码为3的ICMP包则说明目标主机存在。
            if icmp_header.code == 3 and icmp_header.type == 3:
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                    if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message:
                        print("Host Up: %s" % ip_header.src_address)

# Handle CTRL-C
except KeyboardInterrupt:
    # if we're using Windows, turn off promicuous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)