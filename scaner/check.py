import socket
import time

HOST = "ns1.e1.ru"
tcp = [53, 139, 445, 631, 953, 6942, 63342]
udp = [53, 68, 123, 137, 138, 631, 5353, 34521]
tcp2 = [53]


def httpsender(host, port):
    s = socket.socket()
    s.settimeout(1)
    data = b''
    try:
        s.connect((host, port))
        s.send(('GET / HTTP/1.1\r\n'
                'Host: {}\r\n'
                '\r\n').format(host).encode()
              )
        time.sleep(0.5)
        try:
            data = s.recv(1024 * 10).decode('cp1251')
        except socket.error:
            pass
        #print(data)
        s.close()
    except socket.error:
        pass
    if data:
        #print(data)
        print(port, ": HTTP")


def smtpchecker(host, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((host, port))
        sock.send(("HELO SAM" + "\r\n").encode())
        answer = sock.recv(1024).decode()
        print(answer)
        if answer:
            print(port, "SMTP")
        else:
            pass
            #print(port, "not SMTP")
    except socket.error:
        pass
        #print(port, "not SMTP")

def pop3checker(host, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((host, port))
        sock.send(("USER admin" + "\r\n").encode())
        answer = sock.recv(1024).decode()
        print(answer)
        if answer:
            print(port, "Pop3")
        else:
            pass
            #print(port, "not Pop3")
    except socket.error:
        pass
        #print(port, "not Pop3")

def dnschecker(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        with open("dnsquery", "rb") as f:
            data = f.read()
        sock.sendto(data, (host, port))
        data2, _ = sock.recvfrom(2**16)
        if data2:
            print(port, ":DNS")
    except socket.error:
        pass

def ntpchecker(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        with open("ntpquery", "rb") as f:
            data = f.read()
        sock.sendto(data, (host, port))
        data2, _ = sock.recvfrom(2 ** 16)
        print(data2)
        if data2:
            print(port, ":NTP")
    except socket.error:
        pass


def check():
    for port in tcp2:
        ntpchecker(HOST, port)
        smtpchecker(HOST, port)
        pop3checker(HOST, port)
        dnschecker(HOST, port)
        httpsender(HOST, port)



if __name__ == "__main__":
    check()