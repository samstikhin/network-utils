import sys
import re
import socket
import subprocess
import argparse
from urllib.request import urlopen


def get_info(ip):
    with socket.socket() as s:
        whois = get_whois(ip)
        ip += '\n' #чтобы не зависал буфер
        result = ''
        try:
            s.connect((whois, 43))
            s.send(ip.encode())
            while True:
                buffer = s.recv(4096)
                if buffer:
                    result += buffer.decode()
                else:
                    break
            return result
        except Exception:
            return 'failed'


def get_whois(ip):
    with urlopen('http://www.iana.org/whois?q='+ip) as page:
        page = page.readall().decode()
        try:
            return re.search(r'whois:.+', page).group().split()[-1]
        except Exception:
            return 'failed'


def get_provider(ip):
    with urlopen('https://www.whoismyisp.org/ip/' + ip) as page:
        page = page.readall().decode()
        try:
            prov = re.search(r'<h1>.+</h1>', page)
            return prov.group(0)[4:-5]
        except:
            'failed'


def tracert(domain):
    output = subprocess.check_output('traceroute ' + domain, shell=True)
    lines = output.decode().split('\n')[1:]
    addreses = []
    for line in lines:
        try:
            mo = re.search(r' *(\d+).*(\(\d+\.\d+\.\d+\.\d+\))', line)
            addreses.append((mo.group(1), mo.group(2)[1:-1]))
        except Exception:
            continue
    return addreses


def get_country(info):
    mo = re.search(r'country:.+', info)
    if mo:
        return mo.group().split()[-1]
    else:
        return 'undefine'


def get_asnumber(info):
    mo = re.search(r'origin:.+', info)
    if mo:
        return mo.group().split()[-1]
    else:
        return 'undefine'


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('domain', help="write domain", type=str)
    return parser


def main():
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    domain = namespace.domain
    ip_tuples = tracert(domain)
    for ip_tup in ip_tuples:
        ip = ip_tup[1]
        number = ip_tup[0]
        info = get_info(ip)
        country = get_country(info)
        asnumber = get_asnumber(info)
        provider = get_provider(ip)
        whois = get_whois(ip)
        line = '{0:<4} IP:{1:<15} AS:{2:<10} Country:{3:<10} Whois:{5:<20}' \
               'Provider:{4:<50}'.\
            format(number, ip, asnumber, country, provider, whois)
        print(line)


if __name__ == '__main__':
    main()
