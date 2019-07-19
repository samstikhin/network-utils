import struct
import socket


class DNSException(Exception):
    pass


class DNSHeader:
    HEADER_PACKET_FORMAT = "!6H"

    def __init__(self, qr=0, rcode = 0, ancount=0, qdcount=1):
        self.id = 0
        self.flags = 0
        self.qr = qr
        self.opcode = 0
        self.authoritative = 0
        self.tc = 0
        self.rd = 0
        self.ra = 0
        self.z = 0
        self.ansauth = 0
        self.nonauth = 0
        self.rcode = rcode
        self.qdcount = qdcount
        self.ancount = ancount
        self.nscount = 0
        self.arcount = 0

    def to_data(self):
        try:
            packed = struct.pack(DNSHeader.HEADER_PACKET_FORMAT,
                                 self.id,
                                 (self.qr << 15 |
                                  self.opcode << 11 |
                                  self.authoritative << 10 |
                                  self.tc << 9 |
                                  self.rd << 8 |
                                  self.ra << 7 |
                                  self.z << 6 |
                                  self.ansauth << 5 |
                                  self.rcode << 4),
                                 self.qdcount,
                                 self.ancount,
                                 self.nscount,
                                 self.arcount)
        except struct.error:
            raise DNSException("Invalid DNS packet fields.")
        return packed

    def from_data(self, data):
        query_head_length = struct.calcsize(DNSHeader.HEADER_PACKET_FORMAT)
        try:
            header = struct.unpack(DNSHeader.HEADER_PACKET_FORMAT,
                                   data[0:query_head_length])
        except struct.error:
            raise Exception("Invalid DNSheader fields.")
        self.id = header[0]
        self.flags = header[1]
        self.qr = header[1] >> 15 & 0x1
        self.opcode = header[1] >> 11 & 0x15
        self.authoritative = header[1] >> 10 & 0x1
        self.tc = header[1] >> 9 & 0x1
        self.rd = header[1] >> 8 & 0x1
        self.ra = header[1] >> 7 & 0x1
        self.z = header[1] >> 6 & 0x1
        self.ansauth = header[1] >> 5 & 0x1
        self.nonauth = header[1] >> 4 & 0x1
        self.rcode = header[1] & 0x15
        self.qdcount = header[2]
        self.ancount = header[3]
        self.nscount = header[4]
        self.arcount = header[5]

    def __str__(self):
        return "Transaction ID: {} {}\n".format(hex(self.id), self.id) +\
               "Flags: {}\n".format(hex(self.flags)) + \
               "QR: {}\n".format(self.qr) + \
               "Opcode: {}\n".format(self.opcode) + \
               "Authorative: {}\n".format(self.authoritative) + \
               "Truncked: {}\n".format(self.tc) + \
               "Recursion desired: {}\n".format(self.rd) + \
               "Recursion available: {}\n".format(self.ra) + \
               "Z: {}\n".format(self.z) + \
               "Answer authenticated: {}\n".format(self.ansauth) + \
               "Not auth data: {}\n".format(self.nonauth) + \
               "Rcode: {}\n".format(self.rcode) + \
               "Questions: {}\n".format(self.qdcount) +\
               "Answers: {}\n".format(self.ancount) +\
               "Authority: {}\n".format(self.nscount) +\
               "Additional: {}\n".format(self.arcount)


class DNSQuery:

    def __init__(self, name="", type=0, clazz=0):
        self.name = name
        self.type = type
        self.clazz = clazz

    def from_data(self, data):
        header_length = struct.calcsize(DNSHeader.HEADER_PACKET_FORMAT)
        it = header_length
        self.name, it = read_domain(data, it)
        self.type, self.clazz = struct.unpack("!HH", data[it:it + struct.calcsize("!HH")])
        it += struct.calcsize("!HH")
        return it

    def __str__(self):
        return "Query:\n" \
               "Domain name: {domain_name}\n" \
               "Type: {type}\n" \
               "Class: {qclass}\n".format(domain_name=self.name,
                                          type=DNSPacket.TYPES[self.type],
                                          qclass=DNSPacket.CLASSES[self.clazz])

    def __eq__(self, other):
        if str(self) == str(other):
            return True
        return False


class DNSResponse():

    def __init__(self, record="", name="", type=0, clazz=1, ttl=0, data_length=0,
                 address="", ns="", cname="", preference=0, mailexchange="", txt_length=0, txt="",
                 mailbox="", serial_num=0, refresh_int=0, retry_int=0, expire=0, minttl=0):
        self.record = record

        self.name = name
        self.type = type
        self.clazz = clazz
        self.ttl = ttl
        self.data_length = data_length

        self.ns = ns
        self.address = address
        self.cname = cname

        self.preference = preference
        self.mailexchange = mailexchange

        self.txt_length = txt_length
        self.txt = txt

        self.mailbox = mailbox
        self.serial_num = serial_num
        self.refresh_int = refresh_int
        self.retry_int = retry_int
        self.expire = expire
        self.minttl = minttl

    def from_data(self, data, it):
        self.name, it = read_domain(data, it)
        self.type, \
        self.clazz, \
        self.ttl, \
        self.data_length = \
            struct.unpack("!HHIH",
                          data[it:it + struct.calcsize("!HHIH")])
        it += struct.calcsize("!HHIH")
        if self.type == 1:
            self.address = socket.inet_ntoa(data[it:it + 4])
            it+=4
        if self.type == 28:
            self.address = socket.inet_ntop(socket.AF_INET6, data[it:it + 8])
            it+=8
        if self.type == 5:
            self.cname, it = read_domain(data, it)
        if self.type == 2:  # NS
            self.ns, it = read_domain(data, it)
        if self.type == 6:  #SOA
            self.ns, it = read_domain(data, it)
            self.mailbox, it = read_domain(data, it)
            self.serial_num, \
            self.refresh_int, \
            self.retry_int, \
            self.expire, \
            self.minttl = struct.unpack("!5I", data[it:it+struct.calcsize("!5I")])
            it += struct.calcsize("!5I")
        return it

    def __str__(self):
        line = "{record}:\n" \
               "Domain name: {domain_name}\n" \
               "Type: {type}\n" \
               "Class: {rclass}\n" \
               "TTL: {ttl}\n" \
               "Data length: {data_length}\n".format(record=self.record,
                                                     resp_type=self.type,
                                                     domain_name=self.name,
                                                     type=DNSPacket.TYPES[self.type],
                                                     rclass=DNSPacket.CLASSES[self.clazz],
                                                     ttl=self.ttl,
                                                     data_length=self.data_length)
        if self.type == 1 or self.type==28:
            line += "Addresse: {}\n".format(self.address)
        if self.type == 5:
            line += "Canonical name: {}\n".format(self.cname)
        if self.type == 2:
            line += "Name Server: {}\n".format(self.ns)
        if self.type == 6:
            line += "Name Server: {ns}\n" \
                    "Mailbox: {mailbox}\n " \
                    "Serial number: {serial}\n " \
                    "Refresh Interval: {refresh}\n " \
                    "Retry Interval: {retry}\n " \
                    "Expire: {expire}\n " \
                    "Min TTL: {minttl}\n".format(ns=self.ns,
                                                 mailbox=self.mailbox,
                                                 serial=self.serial_num,
                                                 refresh=self.refresh_int,
                                                 retry=self.retry_int,
                                                 expire=self.expire,
                                                 minttl=self.minttl)

        return line


class DNSPacket:
    TYPES = {0: 'default', 1: 'A', 28: "AAAA", 5: "CNAME", 2: "NS", 12:"PTR", 6:"SOA", 15:"MX", 16:"TXT", 13:"HINFO"}
    CLASSES = {0: "default", 1: 'IN'}

    def __init__(self, qr=0, rcode=0, ancount=0, qdcount=1, domain="", type=0, clazz=1):
        self.header = DNSHeader(qr, rcode, ancount, qdcount)
        self.query = DNSQuery(name=domain, type=type, clazz=clazz)
        self.responses = []

    def to_data_good(self):
        try:
            it = 0
            names = {}
            packed = b''
            packed += self.header.to_data()

            it += struct.calcsize(DNSHeader.HEADER_PACKET_FORMAT)

            dom_pack, it = extend_domain_to_bat(self.query.name, names, packed, it)
            packed += dom_pack

            packed += struct.pack("!HH", self.query.type, self.query.clazz)
            it += struct.calcsize("!HH")

            for resp in self.responses:
                dom_pack, it = extend_domain_to_bat(resp.name, names, packed, it)
                packed += dom_pack
                packed += struct.pack("!HHIH",
                                      resp.type,
                                      resp.clazz,
                                      resp.ttl,
                                      resp.data_length)
                it += struct.calcsize("!HHIH")

                if resp.type == 1:
                    packed += socket.inet_aton(resp.address)
                    it+=4
                if resp.type == 28:
                    packed += socket.inet_pton(socket.AF_INET6, resp.address)
                    it+=8
                if resp.type == 5:
                    dom_pack, it = extend_domain_to_bat(resp.cname, names, packed, it)
                    packed += dom_pack
                if resp.type == 2:
                    dom_pack, it = extend_domain_to_bat(resp.ns, names, packed, it)
                    packed += dom_pack

                if resp.type == 6:
                    dom_pack, it = extend_domain_to_bat(resp.ns, names, packed, it)
                    packed += dom_pack
                    dom_pack, it = extend_domain_to_bat(resp.mailbox, names, packed, it)
                    packed += dom_pack
                    packed += struct.pack("!5I",
                                          resp.serial_num,
                                          resp.refresh_int,
                                          resp.retry_int,
                                          resp.expire,
                                          resp.minttl)
                    it+=struct.calcsize("!5I")
        except struct.error:
            raise Exception
        return packed

    def from_data(self, data):
        self.header.from_data(data)
        it = self.query.from_data(data)
        iter_of_resp = 0
        if self.header.qr == 1:
            while it < len(data):
                iter_of_resp += 1
                if iter_of_resp <= self.header.ancount:
                    resp = DNSResponse("Answer")
                elif iter_of_resp <= self.header.ancount + self.header.nscount:
                    resp = DNSResponse("Authorative nameserver")
                else:
                    resp = DNSResponse("Additional Records")
                it = resp.from_data(data, it)
                self.responses.append(resp)

    def __str__(self):
        return str(self.header) + "\n" +\
               str(self.query) + "\n" + \
               '\n'.join([str(resp) for resp in self.responses]) + "\n"


def extend_domain_to_bat(name, names, packed, it):
    dom_pack = b''
    domains = name.split('.')
    for domain in domains:
        if domain in names:
            it2 = names[domain]
            dom_pack += struct.pack("!H", ((3 << 6)*(2**8) + it2))
            it+=2
            break
        else:
            names[domain] = it
            dom_pack += struct.pack("!B", len(domain)) + \
                        struct.pack("!{}s".format(len(domain)), domain.encode())
            it += (len(domain) + 1)
    return (dom_pack, it)


def read_domain(data, it):
    word_length = data[it]
    it += 1
    domain = ""
    while (word_length != 0 and word_length >> 6 & 0x3 != 3):
        domain += struct.unpack("!{}s".format(word_length),
                                data[it:it + word_length])[0].decode() + \
                  '.'
        it += word_length
        word_length = data[it]
        it += 1
    if (word_length >> 6 & 0x3 == 3):
        offset = (word_length & 63)*(2**8) + data[it]
        it += 1
        domain += read_domain(data, offset)[0]
    return (domain, it)


def main():
    with open('dnsresp3', 'rb') as bat:
        data = bat.read()
    packet = DNSPacket()
    packet.from_data(data)
    print(packet)
    print(data)
    data2 = packet.to_data_good()
    print(data2)
    pack2 = DNSPacket()
    pack2.from_data(data2)
    print(pack2)

if __name__ == "__main__":
    main()
