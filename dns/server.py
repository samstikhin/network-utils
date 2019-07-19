import socket
from dnspacket import DNSPacket, DNSResponse
import time
import json

A_SERVER = ("ns1.e1.ru", 53)




def save_cache(cache):
    with open("cache.txt", "w") as f:
        f.write(str(cache))


def open_cache():
    with open("cache.txt", "r") as f:
        data = f.read()
    print(data)
    cache = eval(data)
    return cache


def refresh_cache(cache):
    for record in cache:
        ttl = cache[record]["ttl"]
        old_date = cache[record]["date"]
        new_date = time.time()
        diff = new_date-old_date
        if ttl < diff:
            cache.pop(record)
        else:
            cache[record]["ttl"] = int(ttl - diff)
            cache[record]["date"] = new_date
    save_cache(cache)
    print("CACHE")
    print(cache)


def main():
    cache = open_cache()
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock_server.bind(("localhost", 16000))

    while True:
        print("Listening")
        client_data, client_addr = sock_server.recvfrom(2**16)

        refresh_cache(cache)

        query = DNSPacket()
        query.from_data(client_data)
        domain = query.query.name
        type = query.query.type
        clazz = query.query.clazz
        print(domain, type)

        if domain in cache:
            answer = get_answer_from_CACHE(domain, type, cache)
            print("FROM CACHE")
            print(answer)

            data2 = answer.to_data_good()
            print(data2)
            sock_server.sendto(data2, client_addr)
            print(cache)
            refresh_cache(cache)
        else:
            conn = True
            sock_client.sendto(client_data, A_SERVER)
            try:
                server_data, server_addr = sock_client.recvfrom(2**16)
            except socket.error:
                conn = False
            if conn:
                sock_server.sendto(server_data, client_addr)

                response = DNSPacket()
                response.from_data(server_data)
                print("server response")
                print(response)
                add_info_to_CACHE(response, cache)
                refresh_cache(cache)
            else:
                nonvalid = DNSPacket(qr=1, qdcount=1, ancount=0, domain=domain, type=type, rcode=5)
                print("nonvalid packet")
                sock_server.sendto(nonvalid.to_data_good(), client_addr)


def add_info_to_CACHE(response, cache):
    for resp in response.responses:
        if resp.name not in cache:
            cache[resp.name] = {"date": time.time(),
                                "ttl": resp.ttl}
            cache[resp.name]["ns"] = []
            cache[resp.name]["addresses"] = []
            cache[resp.name]["AAAAaddresses"] = []
        if resp.type == 1:
            cache[resp.name]["addresses"].append(resp.address)
        if resp.type == 28:
            cache[resp.name]["AAAAaddress"].append(resp.address)
        if resp.type == 5:
            cache[resp.name]["cname"] = resp.cname
        if resp.type == 2:
            cache[resp.name]["ns"].append(resp.ns)

        if resp.type == 6:
            cache[resp.name]["primary_ns"] = resp.ns
            cache[resp.name]["mailbox"] = resp.mailbox
            cache[resp.name]["serial"] = resp.serial_num
            cache[resp.name]["refresh"] = resp.refresh_int
            cache[resp.name]["retry"] = resp.retry_int
            cache[resp.name]["expire"] = resp.expire
            cache[resp.name]["minttl"] = resp.minttl
    print(cache)


def get_answer_from_CACHE(name, type, cache):
    answer = DNSPacket(qr=1, qdcount=1, ancount=1, domain=name, type=type)
    nonvalid = DNSPacket(qr=1, qdcount=1, ancount=0, domain=name, type=type, rcode = 5)
    valid = True
    ttl = cache[name]["ttl"]

    if type == 1:
        try:
            addresses = cache[name]["addresses"]
            for addr in addresses:
                response = DNSResponse(record="answer", name=name, type=type, address=addr, ttl=ttl, data_length=4)
                answer.responses.append(response)
        except KeyError:
            valid = False
    if type == 28:
        try:
            AAAAaddresses = cache[name]["AAAAaddresses"]
            for addr in AAAAaddresses:
                response = DNSResponse(record="answer", name=name, type=type, address=addr, ttl=ttl, data_length=8)
                answer.responses.append(response)
        except KeyError:
            valid = False
    if type == 5:
        try:
            cname = cache[name]["cname"]
            response = DNSResponse(record="answer", name=name, type=type, cname=cname, ttl=ttl, data_length=len(cname))
            answer.responses.append(response)
        except KeyError:
            valid = False
    if type == 2:
        try:
            nss = cache[name]["ns"]
            for ns in nss:
                response = DNSResponse(record="answer", name=name, type=type, ns=ns, ttl=ttl, data_length=len(ns))
                answer.responses.append(response)
        except KeyError:
            valid = False

    if type == 6:
        try:
            prime_ns = cache[name]["primary_ns"]
            mailbox = cache[name]["mailbox"]
            serial = cache[name]["serial"]
            refresh = cache[name]["refresh"]
            retry = cache[name]["retry"]
            expire = cache[name]["expire"]
            minttl = cache[name]["minttl"]
            response = DNSResponse(record="answer", name=name, type=type, ttl=ttl, data_length=len(prime_ns)+len(mailbox)+20,
                                   ns=prime_ns, mailbox=mailbox, serial_num=serial, refresh_int=refresh,
                                   retry_int=retry, expire=expire, minttl=minttl)
            answer.responses.append(response)
        except KeyError:
            valid = False

    if valid:
        return answer
    else:
        return nonvalid


if __name__ == "__main__":
    main()

