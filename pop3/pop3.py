import socket
import ssl
import re
import sys
import base64
import os


def is_ok(ans):
    if re.match('\+OK', ans):
        return True
    print("Something bad")
    sys.exit(0)


def send_command(sock, command, value='', extra=''):
    sock.send('{command} {value} {extra}\r\n'.format(command=command, value=value, extra=extra).encode())
    ans = sock.recv(2 ** 16).decode()
    print(ans)
    is_ok(ans)
    return ans


def main():
    HOST = "pop3.mail.ru"
    PORT = 995
    LOGIN = "****@mail.ru"
    PASSWD = "*****"
    sock = socket.create_connection((HOST, PORT))
    sock = ssl.wrap_socket(sock)
    sock.settimeout(1)
    ans = sock.recv(2**16).decode()
    print(ans)
    is_ok(ans)
    print("Connected")

    send_command(sock, "USER", LOGIN)
    send_command(sock, "PASS", PASSWD)
    ans = send_command(sock, "STAT")
    stats = ans.split()
    numb_of_msgs = int(stats[1])
    sum_size = int(stats[2])
    print('Number of messages: {}'.format(numb_of_msgs))
    print('Summary size: {}'.format(sum_size))

    for number_of_message in range(1, numb_of_msgs+1):
        ans = send_command(sock, "LIST", str(number_of_message))
        ans = sock.send("RETR {} \r\n".format(number_of_message).encode())
        print(ans)
        msg_data = b''
        data = sock.recv(2 ** 16)
        while data:
            msg_data += data
            try:
                data = sock.recv(2 ** 16)
            except socket.error:
                break

        info = msg_parser(str(msg_data)[2:-1])
        create_folders(info, number_of_message)


def msg_parser(msg_data):
    lines = msg_data.split("\\r\\n")
    info = {"attachments": []}
    for line in lines:
        if re.match(r"Subject", line):
            info["subject"] = line
        if re.match(r"Date", line):
            info["date"] = line
        if re.match(r"From", line):
            info["sender"] = line
    mo_data = re.search(r'base64\\r\\n\\r\\n(.*?)\\r\\n', msg_data, re.DOTALL)
    if mo_data:
        info["data"] = base64.b64decode(mo_data.group(1)).decode()
    iter = re.finditer(r"attachment; filename=\"(.*?)\"(.*?)--", msg_data, re.DOTALL)
    for mo_att in iter:
        info["attachments"].append((mo_att.group(1),
                                    base64.b64decode(bytes(mo_att.group(2).replace("\\r\\n", ""), 'utf-8'))))
    return info


def create_folders(info, number_of_message):
    try:
        os.makedirs("message{}".format(number_of_message))
    except:
        pass
    with open("message{}/message_info.txt".format(number_of_message), 'w') as file:
        file.write("{}\n{}\n{}\n{}".format(info["subject"],
                                           info["date"],
                                           info["sender"],
                                           info["data"]))
    for attachment in info["attachments"]:
        with open("message{}/{}".format(number_of_message, attachment[0]), 'wb') as file:
            file.write(attachment[1])


if __name__ == '__main__':
    main()
