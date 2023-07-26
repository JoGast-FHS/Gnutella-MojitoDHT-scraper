import signal
import socket
import time
from queue import Queue
from src.Gnutella import Gnutella_ConnectMessage
from src.Gnutella import Gnutella_GnutellaPacket
from src._general_ import _utilities_
from src._general_._timeoutHandler_ import timeout
from config import _config
from config import _targets



def do_handshake(sock, target):
    local_ip = _utilities_.get_public_ip(_config.gnutella_sending_ipVer)
    local_port = sock.getsockname()[1]
    foundIPs = []

    messageString = Gnutella_ConnectMessage.ConnectMessage.handshakePacket(target[0]).toString()
    sock.sendall(messageString.encode())
    responseString = sock.recv(1024).decode()
    gnutellaResponse = Gnutella_ConnectMessage.ConnectMessage(responseString)
    if gnutellaResponse.statusCode == 200:
        print("200 - OK... sending ACK\n")
        gnutellaAck = Gnutella_ConnectMessage.ConnectMessage.ackPacket().toString()
        sock.sendall(gnutellaAck.encode())
        return (0, [])
    elif gnutellaResponse.statusCode == 503:
        if 'X-Try' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['X-Try'].split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                foundIPs.append(ipTuple[0], ipTuple[1])
            print(f"503 - Got IPs: {foundIPs}\n")
        elif 'X-Try-Hubs' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['X-Try-Hubs'].split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                foundIPs.append((ipTuple[0], ipTuple[1].split(' ')[0]))
            print(f"503 - Got Hub-IPs: {foundIPs}\n")
        return (1, foundIPs)
    else:
        print(f"Unknown banner: < {gnutellaResponse.banner} >\n")
        return (2, [])


#@timeout(_config.gnutella_socket_timeout - 2)
def timedRecv(sock, buf):
    return sock.recv(buf)


def ping(sock, target):
    ret = (-1, [])
    try:
        sock.connect(target)
        timedRecv_f = timeout(_config.gnutella_socket_timeout - 3)(timedRecv)
        handshakeResp = do_handshake(sock, target)
        ret = handshakeResp
        if handshakeResp[0] == 0:
            try:
                while True:
                    peerResp = timedRecv_f(sock, 1024)
                    #print(f"Peerdata: {peerResp.decode()}\n")  # verbose
            except UserWarning:
                print("recv timeout\n")  # verbose
            ping_message = Gnutella_GnutellaPacket.GnutellaPacket.crawlerPingv4().toString()
            ping_bytes = bytearray.fromhex(ping_message)
            #time.sleep(3)
            sock.sendall(ping_bytes)
            while True:
                pong_bytes = sock.recv(1024)
                #print(f"Pong: {pong_bytes.decode()}\n")
    except socket.timeout:
        print(f"Error while pinging {target}: Timeout\n")
    except ConnectionError:
        print(f"Error while pinging {target}: Connection failed\n")
    except UnicodeDecodeError:
        print(f"Error while decoding response from {target}\n")
    return ret


def gnutellaPings(targets):
    if _config.gnutella_sending_ipVer == 4:
        family = socket.AF_INET
    else:
        family = socket.AF_INET6

    foundIPs = []
    for target in targets:
        sock = socket.socket(family=family, type=socket.SOCK_STREAM)
        sock.bind((_utilities_.get_local_ip(_config.gnutella_sending_ipVer), 0))
        sock.settimeout(_config.gnutella_socket_timeout)
        print(f"{sock.getsockname()[0]}:{sock.getsockname()[1]} --> {target[0]}:{target[1]}")  # verbose
        retCode, ips = ping(sock, target)
        if retCode == 1:
            for ip in ips:
                foundIPs.append((ip[0], int(ip[1])))
        sock.close()
        time.sleep(15)
    return foundIPs


def gnutellaInitPings():
    if _config.gnutella_sending_ipVer == 4:
        return gnutellaPings(_targets.gnutella_targets_ipv4)
    else:
        return gnutellaPings(_targets.gnutella_targets_ipv6)


def initGnutella():
    pingQueue = Queue(maxsize=10000)
    foundIPs = gnutellaInitPings()
    for ip in foundIPs:
        pingQueue.put(ip)
        print(f"{ip} put in Queue.")
    return pingQueue