import socket
import struct
import time
import datetime


def system_to_ntp_time(timestamp):
    return timestamp + NTPPacket.NTP_DELTA

def ntp_to_system_time(timestamp):
    return timestamp - NTPPacket.NTP_DELTA

def to_frac(timestamp, n=32):
    return int(abs(timestamp - int(timestamp)) * 2**n)


def to_time(integral_part, fraction_part, n=32):
    return integral_part + float(fraction_part)/2**n


class NTPException(Exception):
    pass


class NTPPacket:
    _SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])

    _NTP_EPOCH = datetime.date(1900, 1, 1)

    NTP_DELTA = (_SYSTEM_EPOCH - _NTP_EPOCH).days * 24 * 3600

    _PACKET_FORMAT = "!BBBb11I"

    def __init__(self, leap=0, version=4, mode=4, stratum=0,poll=0,precision=0,root_delay=0,
                 root_dispersion=0, ref_id=0, ref_tmstmp=0, orig_tmstmp=0, recv_tmstmp=0, tx_tmstmp=0):
        self.leap = leap
        self.version = version
        self.mode = mode
        self.stratum = stratum
        self.poll = poll
        self.precision = precision
        self.root_delay = root_delay
        self.root_dispersion = root_dispersion
        self.ref_id = ref_id
        self.ref_timestamp = ref_tmstmp
        self.orig_timestamp = orig_tmstmp
        self.origin_timestamp_int = 0
        self.origin_timestamp_frac = 0
        self.recv_timestamp = recv_tmstmp
        self.transmit_timestamp = tx_tmstmp
        self.transmit_timestamp_int = 0
        self.transmit_timestamp_frac = 0

    def to_data(self):
        try:
            packed = struct.pack(NTPPacket._PACKET_FORMAT,
                                 (self.leap << 6 | self.version << 3 | self.mode),
                                 self.stratum,
                                 self.poll,
                                 self.precision,
                                 int(self.root_delay) << 16 | to_frac(self.root_delay, 16),
                                 int(self.root_dispersion) << 16 | to_frac(self.root_dispersion, 16),
                                 self.ref_id,
                                 int(self.ref_timestamp),
                                 to_frac(self.ref_timestamp),
                                 int(self.orig_timestamp),
                                 to_frac(self.orig_timestamp),
                                 int(self.recv_timestamp),
                                 to_frac(self.recv_timestamp),
                                 int(self.transmit_timestamp),
                                 to_frac(self.transmit_timestamp))
        except struct.error:
            raise NTPException("Invalid NTP packet fields.")
        return packed

    def from_data(self, data):
        try:
            unpacked = struct.unpack(NTPPacket._PACKET_FORMAT,
                                     data[0:struct.calcsize(NTPPacket._PACKET_FORMAT)])
        except struct.error:
            raise NTPException("Invalid NTP packet.")

        self.leap = unpacked[0] >> 6 & 0x3
        self.version = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.stratum = unpacked[1]
        self.poll = unpacked[2]
        self.precision = unpacked[3]
        self.root_delay = float(unpacked[4])/2**16
        self.root_dispersion = float(unpacked[5])/2**16
        self.ref_id = unpacked[6]
        self.ref_timestamp = to_time(unpacked[7], unpacked[8])
        self.orig_timestamp = to_time(unpacked[9], unpacked[10])
        self.origin_timestamp_int = unpacked[9]
        self.origin_timestamp_frac = unpacked[10]
        self.recv_timestamp = to_time(unpacked[11], unpacked[12])
        self.transmit_timestamp = to_time(unpacked[13], unpacked[14])
        self.transmit_timestamp_int = unpacked[13]
        self.transmit_timestamp_frac = unpacked[14]


    def __str__(self):
        return "ntp PACKET:\n" +\
               "Leap:{}\n".format(self.leap) +\
               "Version:{}\n".format(self.version) +\
               "Mode:{}\n".format(self.mode) +\
               "stratum:{}\n".format(self.stratum) +\
               "poll:{}\n".format(self.poll) +\
               "precision:{}\n".format(self.precision) +\
               "root_delay:{}\n".format(self.root_delay) +\
               "root_dispersion:{}\n".format(self.root_dispersion) +\
               "ref_id:{}\n".format(self.ref_id) +\
               "ref_timestamp:{}\n".format(
                   datetime.datetime.fromtimestamp(
                       ntp_to_system_time(self.ref_timestamp))) +\
               "orig_timestamp:{}\n".format(
                   datetime.datetime.fromtimestamp(
                       ntp_to_system_time(self.orig_timestamp))) +\
               "recv_timestamp:{}\n".format(
                   datetime.datetime.fromtimestamp(
                       ntp_to_system_time(self.recv_timestamp))) +\
               "transmit_timestamp:{}\n".format(
                   datetime.datetime.fromtimestamp(
                       ntp_to_system_time(self.transmit_timestamp)))

PORT = 123
HOST = "localhost"

def main():
    with open("ntpbat", "rb") as f:
        data = f.read()
    packet = NTPPacket()
    packet.from_data(data)
    print(packet)

if __name__ == "__main__":
    main()