import socket
import ntpserver
import time
import datetime

HOST = "localhost"
PORT = 123


def main():
    offset = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    query = ntpserver.NTPPacket()
    while True:
        print("Listen")
        query_data, addr = sock.recvfrom(2**16)
        recv_time = ntpserver.system_to_ntp_time(time.time())
        query.from_data(query_data)
        print(query)
        response = ntpserver.NTPPacket(poll=3,
                                       precision=-23,
                                       root_delay=0.022674560546875,
                                       stratum=2,
                                       version=query.version,
                                       root_dispersion=0.032196044921875,
                                       ref_id=1921680102,
                                       ref_tmstmp=recv_time,
                                       orig_tmstmp=query.transmit_timestamp,
                                       recv_tmstmp=recv_time,
                                       )
        send_time = time.time() + offset
        response.transmit_timestamp = ntpserver.system_to_ntp_time(send_time)
        print(response)
        try:
            sock.sendto(response.to_data(), addr)
        except socket.error:
            pass

if __name__ == "__main__":
    main()