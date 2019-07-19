#!/usr/bin/env python
import socket
import sys
import argparse
import time
from concurrent.futures import ThreadPoolExecutor


class Timer():
    def __enter__(self):
        self.startTime = time.time()

    def __exit__(self, type, value, traceback):
        print("Total time: {:.3f} sec".format(time.time() - self.startTime))


def find_open_tcp_ports(ip, diapason, thread_count):
    pool = ThreadPoolExecutor(thread_count)
    ports = list(range(diapason[0], diapason[1]))
    open_ports = [port for is_open, port in zip(
            pool.map(lambda x: scan_tcp_port(ip, x), ports), ports) if is_open]
    return open_ports


def scan_tcp_port(ip, port):
    socket.setdefaulttimeout(0.1)
    with socket.socket() as sock:
        try:
            sock.connect((ip, port))
            print("Port {0} Open".format(port))
            return True
        except socket.error:
            return False


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-address', help="write address", type=str, default='localhost')
    parser.add_argument('-d', '--domain', help="write domain",
                        action='store_const', const=True)
    return parser


def main():
    diapason = (18, 130)
    thread_count = 2000
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    if namespace.domain:
        ip = socket.gethostbyname("ns1.e1.ru")
    else:
        ip = namespace.address
    with Timer() as t:
        open_ports = find_open_tcp_ports(ip, diapason, thread_count)
    print("Thread count:{}".format(thread_count))
    print("Open TCP ports: {}".format(open_ports))

if __name__ == '__main__':
    main()