#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
from ctypes import *

HOST = socket.gethostbyname(socket.gethostname())
PORT = 0

class TCP(BigEndianStructure):
    # TCP Header Components
    _fields_ = [("sport",       c_ushort),
                ("dport",       c_ushort),
                ("seq",         c_uint32),
                ("ack",         c_uint32),
                ("doff_reserv", c_ubyte),
                ("cflag",       c_ubyte),
                ("windsize",    c_ushort),
                ("chksum",      c_ushort),
                ("urgpointer",  c_ushort)
            ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass

def main():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    tcp_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    tcp_sock.bind((HOST, PORT))

    try:
        while True:
            raw_buffer = tcp_sock.recvfrom(1024*4)[0]
            # IP Hedaer length
            ihl_length = 5 * 4
            # TCP Header
            tcp_header = TCP(raw_buffer[ihl_length:ihl_length+4*5])
            print "TCP Header"
            print "sport : %d  dport : %d  seq : %d  ack : %d" % (tcp_header.sport,tcp_header.dport, tcp_header.seq, tcp_header.ack)
            print ""
    except socket.error as e:
        print str(e)

if __name__ == '__main__':
    main()
