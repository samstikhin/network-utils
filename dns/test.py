import socket
from dnspacket import DNSPacket
import struct
import time


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    query = DNSPacket(qr=0, qdcount=1, ancount=0, domain="e1.ru.", type=6, clazz=1)
    query.header.rd = 1
    data = query.to_data_good()
    print(query)

    client.sendto(data, ("ns1.e1.ru", 53))
    answer, addr = client.recvfrom(2 ** 16)
    response = DNSPacket()
    response.from_data(answer)
    print(response)

if __name__ == "__main__":
    t1 = time.time()
    time.sleep(1)
    t2 = time.time()
    print(t2-t1)