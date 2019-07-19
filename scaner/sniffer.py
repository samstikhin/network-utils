import socket
import struct
import ctypes
#from ICMPHeader import ICMP

# host to listen
HOST = '127.0.0.1'

class ICMPPacket:
    def __init__(self, buf):
        self.first_ip_head = self.ip_header(buf[0:20])
        self.icmp_head = self.icmp_header(buf[20:28])
        self.sec_ip_head = self.ip_header(buf[28:48])
        self.udp_head = self.udp_header(buf[48:56])
        self.data = buf[56:].decode()

    def __str__(self):
        pass

    def ip_header(self, buf):
        iph = struct.unpack('!BBHHHBBH4s4s', buf)
        ip_head = {}
        ip_head['version_ihl'] = iph[0]
        ip_head['version'] = iph[0] >> 4
        ip_head['header_length'] = iph[0] & 0xF
        ip_head['total_length'] = iph[2]
        ip_head['ttl'] = iph[5]
        ip_head['protocol'] = iph[6]
        ip_head['checksum'] = iph[7]
        ip_head['s_addr'] = socket.inet_ntoa(iph[8])
        ip_head['d_addr'] = socket.inet_ntoa(iph[9])
        return ip_head

    def icmp_header(self, buf):
        icmp_head = {}
        icmp_info = struct.unpack('!BBH4s', buf)
        icmp_head['type'] = icmp_info[0]
        icmp_head['code'] = icmp_info[1]
        icmp_head['checksum'] = icmp_info[2]
        icmp_head['addr'] = socket.inet_ntoa(icmp_info[3])
        return icmp_head

    def udp_header(self, buf):
        udp_info = struct.unpack('!HHHH', buf)
        udp_head = {}
        udp_head['source_port'] = udp_info[0]
        udp_head['dest_port'] = udp_info[1]
        udp_head['length'] = udp_info[2]
        udp_head['checksum'] = udp_info[3]
        return udp_head



def sniffing(host):
    while True:
        sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                socket.IPPROTO_ICMP)
        sniffer.bind((host, 0))
        sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        raw_buffer = sniffer.recvfrom(65565)[0]
        #print(raw_buffer)
        icmp_packet = ICMPPacket(raw_buffer)
        print(icmp_packet.first_ip_head)
        print(icmp_packet.icmp_head)
        print(icmp_packet.sec_ip_head)
        print(icmp_packet.udp_head)
        print(icmp_packet.data)



if __name__ == '__main__':
    sniffing(HOST)