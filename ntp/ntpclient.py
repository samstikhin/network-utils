import time
import socket
import ntpserver


def main():
    packet = ntpserver.NTPPacket()
    packet.transmit_timestamp = ntpserver.system_to_ntp_time(time.time())
    data = packet.to_data()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, ("localhost", 123))
    data2, addr = sock.recvfrom(2**16)
    response = ntpserver.NTPPacket()
    response.from_data(data2)
    print(response)


if __name__ == "__main__":
    main()
