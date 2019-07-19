import threading
import time
import socket
import struct

HOST = "localhost"

def check_ports(port):
    ports = [53, 68, 137, 138, 631, 5353, 40044]


def check_http(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    s.connect((host, port))
    s.send(('GET / HTTP/1.1\r\n'
            'Host: {}\r\n'
            '\r\n').format(host).encode()
           )
    time.sleep(0.5)
    try:
        print(s.recv(1024 * 10).decode('cp1251'))
    except socket.error:
        print(port, "not HTTP")
    s.close()


def udp_sender(ip, diapason):
    for port in range(diapason[0], diapason[1]):
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.sendto(b"Hello", (ip, port))
        sender.close()


def get_port(buf):
    rest = struct.unpack('!HHHH', buf[48:56])
    return rest[1]


def get_icmp_info(buf):
    icmp_header = buf[20:28]
    icmp_info = struct.unpack('BBHHH', icmp_header)
    return(icmp_info[0], icmp_info[1])


def main():
    diapason = (1, 65000)
    ports = [x for x in range(diapason[0], diapason[1])]
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sniffer.bind((HOST, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    sniffer.settimeout(3)
    threading.Thread(target=udp_sender, args=("localhost", diapason)).start()
    while True:
        try:
            raw_buffer = sniffer.recvfrom(2**16)[0]
        except socket.timeout:
            break
        icmp_info = get_icmp_info(raw_buffer)
        code = icmp_info[1]
        type = icmp_info[0]
        port = get_port(raw_buffer)
        if code == 3 and type == 3:
            ports.remove(port)
    print("Open UDP ports:", ports)
    check_ports(ports)

if __name__ == '__main__':
    main()