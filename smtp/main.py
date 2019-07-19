import socket
import ssl
import base64


class Sender:
    def __init__(self, conf_dict):
        self.sock = socket.create_connection((self.det_server(conf_dict["From"]), 465))
        self.sock = ssl.wrap_socket(self.sock)
        self.conf_dict = conf_dict
        self.configurations = get_configurations(conf_dict)

    def det_server(self, sender):
        name, server = sender.split('@')
        return "smtp."+ server


    def sending(self):
        encode_login = bytes_to_b64_str(bytes(self.conf_dict["login"], 'utf-8'))
        encode_password = bytes_to_b64_str(bytes(self.conf_dict["password"], 'utf-8'))
        self.send_command('EHLO Sam')
        self.send_command('AUTH LOGIN')
        self.send_command(encode_login)
        self.send_command(encode_password)
        for configuration in self.configurations:
            msg = create_message(configuration)
            self.send_command('MAIL FROM: <{}>'.format(configuration["From"]))
            self.send_command('RCPT TO: <{}>'.format(configuration["To"]))
            self.send_command('DATA')
            ans = self.send_msg(msg)
            print(ans)
        self.send_command('QUIT')

    def send_command(self, command):
        print(command)
        self.sock.send((command + "\r\n").encode())
        answer = self.sock.recv(1024).decode()
        print(answer)
        return answer

    def send_msg(self, msg):
        self.sock.send((str(msg) + '\r\n.\r\n').encode('utf8'))
        answer = self.sock.recv(1024).decode("utf-8")
        return answer


def bytes_to_b64_str(bdata):
    return str(base64.b64encode(bdata))[2:-1]


def parse_conf_file(filename):
    with open(filename) as conf:
        conf = conf.read()
    headers = conf.split('\n')
    conf_dict = {}
    print(headers)
    for header1 in headers:
        if not header1:
            continue
        header, value = header1.split(': ')
        if header == "To":
            addressees = value.split()
            conf_dict["To"] = []
            for addressee in addressees:
                if addressee[-1] == ',' or addressee[-1] == '.':
                    addressee = addressee[:-1]
                conf_dict["To"].append(addressee.strip())
        elif header == "attachments":
            attachments = value.split()
            conf_dict["attachments"] = []
            for attachment in attachments:
                if attachment[-1] == ',' or attachment[-1] == '.':
                    attachment = attachment[:-1]
                conf_dict["attachments"].append(attachment.strip())
        else:
            conf_dict[header.strip()] = value.strip()
    return conf_dict


def get_configurations(conf_dict):
    configurations = []
    headers = conf_dict.keys()
    for addressee in conf_dict["To"]:
        configuration = {}
        for header in headers:
            if header != "To":
                configuration[header] = conf_dict[header]
            else:
                configuration[header] = addressee
        configurations.append(configuration)
    return configurations


def get_file(filename):
    try:
        with open(filename, "rb") as file:
            file = file.read()
        return file
    except (FileExistsError, FileNotFoundError):
        raise Exception


def create_message(configuration):
    data = get_file(configuration["data"])
    boundary = "===============5049185429753157390=="
    return create_header(configuration, boundary) +\
           create_data(data, boundary) + \
           ''.join(create_attachment(attachment, boundary) for attachment in configuration["attachments"])


def create_header(configuration, boundary):
    encode_login = bytes_to_b64_str(bytes(configuration["login"], 'utf-8'))
    encode_password = bytes_to_b64_str(bytes(configuration["password"], 'utf-8'))
    return "Content-Type: multipart/mixed; boundary=\"{}\"\r\n".format(boundary) + \
           "MIME-Version: 1.0\r\n" + \
           "Subject: hi\r\n".format(configuration["Subject"]) + \
           "From: {}\r\n".format(configuration["From"]) + \
           "To: {}\r\n".format(configuration["To"]) + \
           "login: {}\r\n".format(encode_login) + \
           "password: {}\r\n".format(encode_password) + \
           "\r\n" + \
           "--{}\r\n".format(boundary)


def create_data(data, boundary):
    return "Content-Type: text/plain; charset=\"utf-8\"\r\n" + \
           "MIME-Version: 1.0\r\n" + \
           "Content-Transfer-Encoding: base64\r\n\r\n" + \
           "{}\r\n\r\n".format(bytes_to_b64_str(data)) + \
           "--{}\r\n".format(boundary)


def create_attachment(attachment, boundary):
    return "Content-Type: application/octet-stream\r\n" +\
           "MIME-Version: 1.0\r\n" +\
           "Content-Transfer-Encoding: base64\r\n" +\
           "Content-Disposition: attachment; filename=\"{}\"\r\n\r\n".format(attachment) +\
           "{}\r\n\r\n".format(bytes_to_b64_str(get_file(attachment))) +\
           "--{}\r\n".format(boundary)


def main():
    conf_dict = parse_conf_file('conf.txt')
    s = Sender(conf_dict)
    s.sending()

if __name__ == "__main__":
    main()
