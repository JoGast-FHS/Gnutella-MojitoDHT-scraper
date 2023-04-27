# Utility functions used by dht and gnutella messaging

import ipaddress
import json
import requests
import socket



def get_public_ip(ip_ver):
    response = requests.get(f"https://api{ip_ver}.ipify.org?format=json")  # ipv4 addr or ipv6 addr
    json_response = json.loads(response.text)
    publicIP = json_response['ip']
    return publicIP


def get_local_ip(ip_ver):
    if ip_ver == 4:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.settimeout(0)

    if ip_ver == 4:
        try:
            # doesn't even have to be reachable
            sock.connect(("8.8.8.8", 1))
            socket_ip = sock.getsockname()[0]
        except Exception:
            socket_ip = "127.0.0.1"
        finally:
            sock.close()
    else:
        try:
            # doesn't even have to be reachable
            sock.connect(("2001:4860:4860::8888", 1, 0, 0))
            socket_ip = sock.getsockname()[0]
        except Exception:
            socket_ip = "::1"
        finally:
            sock.close()
    return socket_ip


def ip2hex(ip_addr, ip_ver):
    if ip_ver == 4:
        return '{:#x}'.format(ipaddress.IPv4Address(ip_addr))[2:]  # x->Hex, [2:]->0x abschneiden
    return '{:#n}'.format(ipaddress.IPv6Address(ip_addr))[2:]


def hex2ip(ip_addr, ip_ver):
    if ip_ver == 4:
        addr_family = socket.AF_INET
    else:
        addr_family = socket.AF_INET6
    return socket.inet_ntop(addr_family, bytearray.fromhex(ip_addr))