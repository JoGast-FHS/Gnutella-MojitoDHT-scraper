import random
import socket
import time
import zlib

from src.Gnutella import Gnutella_ConnectMessage
from src.Gnutella import Gnutella_GnutellaPacket
from src._general_ import _utilities_
from src._general_._timeoutHandler_ import timeout
from config import _config
from config import _targets


def createGnutellaSocket():
    if _config.gnutella_sending_ipVer == 4:
        family = socket.AF_INET
    else:
        family = socket.AF_INET6
    sock = socket.socket(family=family, type=socket.SOCK_STREAM)
    sock.bind((_utilities_.get_local_ip(_config.gnutella_sending_ipVer), 0))
    sock.settimeout(_config.gnutella_socket_timeout)
    return sock


def processGnutellaError(gnutellaResponse, foundIPs):
    hubIPs = []
    leafIPs = []
    if gnutellaResponse.statusCode == 503:
        if 'X-Try' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['X-Try'].replace(' ', '').replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                foundIPs.append((ipTuple[0], int(ipTuple[1].split(' ')[0])))
            print(f"503 - Got IPs: {foundIPs}\n")
        if 'X-Try-Ultrapeers' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['X-Try-Ultrapeers'].replace(' ', '').replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                foundIPs.append((ipTuple[0], int(ipTuple[1].split(' ')[0])))
            print(f"503 - Got Ultrapeer-IPs: {foundIPs}\n")
        if 'X-Try-Hubs' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['X-Try-Hubs'].replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(' ')[0].split(':')
                foundIPs.append((ipTuple[0], int(ipTuple[1].split(' ')[0])))
            print(f"503 - Got Hub-IPs: {foundIPs}\n")
        if 'Peers' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['Peers'].replace(' ', '').replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                foundIPs.append((ipTuple[0], int(ipTuple[1].split(' ')[0])))
            print(f"503 - Got Peer-IPs: {foundIPs}\n")
            if 'Leaves' in gnutellaResponse.headers:
                tryIPs = gnutellaResponse.headers['Leaves'].replace(' ', '').replace('\r\n', '').split(',')
                for ip in tryIPs:
                    ipTuple = ip.split(':')
                    foundIPs.append((ipTuple[0], int(ipTuple[1].split(' ')[0])))
                print(f"503 - Got Leaf-IPs: {foundIPs}\n")
        hubIPs = foundIPs
    elif gnutellaResponse.statusCode == 593:  # Rare LimeWire 'Hi' Message as response to Crawler-Handshake
        if 'Peers' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['Peers'].replace(' ', '').replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                hubIPs.append((ipTuple[0], int(ipTuple[1].split(' ')[0])))
            print(f"503 - Got Peer-IPs: {foundIPs}\n")
        if 'Leaves' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['Leaves'].replace(' ', '').replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                leafIPs.append((ipTuple[0], int(ipTuple[1].split(' ')[0])))
            print(f"503 - Got Leaf-IPs: {foundIPs}\n")
    else:
         print(f"Unknown banner: < {gnutellaResponse.banner} >\n")
         return 2, []
    return 1, [hubIPs, leafIPs]


def do_handshake(sock, target, crawlerHeader=False, ip6Header=False, noACK=False):
    foundIPs = []

    if crawlerHeader:
        messageString = Gnutella_ConnectMessage.ConnectMessage.handshakePacket_crawler().toString()
    else:
        listenIP = _utilities_.get_public_ip(_config.gnutella_sending_ipVer)
        _, listenPort = sock.getsockname()
        messageString = Gnutella_ConnectMessage.ConnectMessage.handshakePacket(remote_ip=target[0], listen_ip=listenIP, listen_port=listenPort ).toString()
    if ip6Header:
        messageString += _config.gnutella_ip6HeaderString
    messageString += "\r\n"
    sock.sendall(messageString.encode())
    responseString = sock.recv(1024*8).decode()
    gnutellaResponse = Gnutella_ConnectMessage.ConnectMessage(responseString)
    if crawlerHeader:  # crawler handshake
        if gnutellaResponse.statusCode == 200:
            print("200 - OK... Waiting for crawler response\n")
            return 3, [responseString, gnutellaResponse]
        else:
            return processGnutellaError(gnutellaResponse, foundIPs)
    else:  # normal handshake for Ping message etc.
        if gnutellaResponse.statusCode == 200 and not noACK:
            print("200 - OK... sending ACK\n")
            gnutellaAck = Gnutella_ConnectMessage.ConnectMessage.ackPacket().toString() + "\r\n"
            sock.sendall(gnutellaAck.encode())
            return 0, []
        elif noACK:
            if gnutellaResponse.headers['X-Ultrapeer'] == "True":
                return 0, 1
            elif gnutellaResponse.headers['X-Ultrapeer'] == "False":
                return 0, 0
            else:
                return 0, -1
        else:
            return processGnutellaError(gnutellaResponse, foundIPs)


'''
    Checks if G1/G2 Peer is an Ultrapeer or a Leaf
'''
def is_ultrapeer(ipTuple):
    sock = createGnutellaSocket()
    sock.connect(ipTuple)
    handshakeResp = do_handshake(sock=sock, target=ipTuple, crawlerHeader=False, ip6Header=False, noACK=True)
    if handshakeResp[0] == 0:
        ultrapeer = handshakeResp[1]
        if ultrapeer == -1:
            print("No 'X-Ultrapeer'-header found while checking peer status")
        return ultrapeer
    return -2


#@timeout(_config.gnutella_socket_timeout - 2)
def timedRecv(sock, buf):
    tmp = sock.recv(buf)
    #print("Tmp:\r\n" + tmp.decode() + "\r\n")
    return tmp


def ping(sock, target, crawlerHeader=False, ip6Header=False):
    ret = (-1, [])
    try:
        sock.connect(target)
        timedRecv_f = timeout(_config.gnutella_socket_timeout - 3)(timedRecv)
        handshakeResp = do_handshake(sock, target, crawlerHeader, ip6Header)
        ret = handshakeResp
        if handshakeResp[0] == 3 and crawlerHeader:
            stitchedResp = handshakeResp[1][0]
            try:
                while True:
                    responseString = timedRecv_f(sock, 1024).decode()
                    stitchedResp = stitchedResp + responseString
                    #print(f"Peerdata: {peerResp.decode()}\n")  # verbose
            except UserWarning:
                #print("-recv timeout-")  # verbose
                pass

            #foundIPs = []
            hubIPs = []
            leafIPs = []
            gnutellaResponse = Gnutella_ConnectMessage.ConnectMessage(stitchedResp)
            #print(gnutellaResponse)
            tryIPs = gnutellaResponse.headers['Peers'].replace(' ', '').replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                appendIP = (ipTuple[0], int(ipTuple[1].split(' ')[0]))
                hubIPs.append(appendIP)
                #foundIPs.append(appendIP)
            tryIPs = gnutellaResponse.headers['Leaves'].replace(' ', '').replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                appendIP = (ipTuple[0], int(ipTuple[1].split(' ')[0]))
                leafIPs.append(appendIP)
                #foundIPs.append(appendIP)
            print(f"Got Hubs: {hubIPs}")
            print(f"Got Leaves: {leafIPs}\n")
            return 3, [hubIPs, leafIPs]

        elif handshakeResp[0] == 0:
            try:
                # send Ping
                ping_message = Gnutella_GnutellaPacket.GnutellaPacket.crawlerPingv4().toString()
                ping_bytes = zlib.compress(bytearray.fromhex(ping_message))
                sock.sendall(ping_bytes)

                # recv Pong
                while True:
                    hubIPs = []
                    leafIPs = []
                    decompressor = zlib.decompressobj()
                    recv_bytes = sock.recv(1024*2)
                    hexstr = recv_bytes.hex()
                    # print(f"Orig. Hexstr: {hexstr}")  # verbose
                    pong_bytes = [int(hexstr[i:i + 2], 16) for i in range(0, len(hexstr), 2)]
                    decompressed_bytestr = b''
                    decompressed_hexstring = ""
                    for b in pong_bytes:
                        byte = b.to_bytes(1, "big")
                        decompressed_byte = decompressor.decompress(byte)
                        if decompressed_byte != b'':
                            decompressed_bytestr += decompressed_byte
                            decompressed_hexstring += decompressed_byte.hex()
                            # print(decompressed_byte.hex())
                    decompressor.flush()
                    # print(f"Pong decompressed: {decompressed_hexstring}")  # verbose
                    pongPacket = Gnutella_GnutellaPacket.GnutellaPacket.fromString(decompressed_hexstring)
                    if pongPacket.payloadtype == "01" and pongPacket.payloadlen != 0:  # if Pong
                        tmp_packet = pongPacket
                        while True:
                            payload_remainder, ipTuple = tmp_packet.processPayload()
                            ultrapeer = 0
                            try:
                                ultrapeer = is_ultrapeer(ipTuple)
                            except Exception as e:
                                print(f"Exception thrown getting peer status: {e}")  # verbose

                            if ultrapeer == 1:
                                hubIPs.append(ipTuple)
                            else:
                                leafIPs.append(ipTuple)  # note: also peers where status is undetermined are added to leaves!
                            tmp_packet = Gnutella_GnutellaPacket.GnutellaPacket.fromString(payload_remainder)
                            if payload_remainder == "":  # once payload has been fully processed
                                print("\n")
                                return 3, [hubIPs, leafIPs]
                    else:
                        print("Received something other than a Pong - no further processing.")
            except zlib.error:
                print(f"Error compressing/decompressing: zlib Error thrown\n")

    except socket.timeout:
        print(f"Error while pinging {target}: Timeout\n")
    except ConnectionError:
        print(f"Error while pinging {target}: Connection failed\n")
    except UnicodeDecodeError:
        print(f"Error while decoding response from {target}\n")
    except AttributeError:
        print(f"Error while pinging {target}: Message initialization failed (known issue)\n")
    except Exception as e:
        print(f"Unknown error while pinging {target}: {e}\n")
    return ret


def gnutellaPings(target, crawlerHeader=False, ip6Header=False):
    sock = createGnutellaSocket()
    print(f"{sock.getsockname()[0]}:{sock.getsockname()[1]} --> {target[0]}:{target[1]}")  # verbose
    retCode, retIPs = ping(sock, target, crawlerHeader, ip6Header)
    sock.close()
    return retCode, retIPs


# def gnutellaInitPings(crawlerHeader=False, ip6Header=False):
#     if _config.gnutella_sending_ipVer == 4:
#         return gnutellaPings(_targets.gnutella_targets_ipv4, crawlerHeader, ip6Header)
#     else:
#         return gnutellaPings(_targets.gnutella_targets_ipv6, crawlerHeader, ip6Header)


# def initGnutella(crawlerHeader=False, ip6Header=False):
#     pingQueue = Queue(maxsize=10000)
#     writeQueue = Queue(maxsize=10000)
#     foundIPs = gnutellaInitPings(crawlerHeader, ip6Header)
#     for ip in foundIPs:
#         pingQueue.put(ip)
#         print(f"{ip} put in PingQueue.")
#         writeQueue.put(ip)
#         print(f"{ip} put in WriteQueue.\r\n")
#     return pingQueue, writeQueue


def crawlGnutella(run_event, addrQueue, writeQueues, ip6Header=False):
    crawlerHeader = _config.gnutella_crawlerHeader
    v4File_hubs_c, v4File_leaves_c, v6File_hubs_c, v6File_leaves_c, v4File_hubs_p, v4File_leaves_p, v6File_hubs_p, v6File_leaves_p = _utilities_.get_Filenames("gnutella")
    if crawlerHeader:
        v4File_hubs = v4File_hubs_c
        v4File_leaves = v4File_leaves_c
        v6File_hubs = v6File_hubs_c
        v6File_leaves = v6File_leaves_c
    else:
        v4File_hubs = v4File_hubs_p
        v4File_leaves = v4File_leaves_p
        v6File_hubs = v6File_hubs_p
        v6File_leaves = v6File_leaves_p
    writeQueue_hubs = writeQueues[0]
    writeQueue_leaves = writeQueues[1]

    while run_event.is_set():
        fromQueue = False
        if addrQueue.empty():  # fallback to hardcoded addresses
            if _config.gnutella_sending_ipVer == 4:
                addrNum = random.randint(0, (len(_targets.gnutella_targets_ipv4) - 1))  # choose random addr from hardcoded ipv4 addr
                target_addr = _targets.gnutella_targets_ipv4[addrNum]
                print("Address queue empty - probably all IPv4 addresses in Gnutella networks crawled, using only ultrapeers as seeds or using unreachable seed nodes (-> seed manually)...")
            else:
                addrNum = random.randint(0, (len(_targets.gnutella_targets_ipv6) - 1))  # choose random addr from hardcoded ipv6 addr
                target_addr = _targets.gnutella_targets_ipv6[addrNum]
                print("Address queue empty - probably no IPv6 addresses scraped or wrong configuration...")
        else:
            target_addr = addrQueue.get()
            fromQueue = True
        if target_addr == None or target_addr == "" or target_addr == []:
            print("Error: Failed to initialize target address.\n")
            exit(-1)

        retCode, ips = gnutellaPings(target=target_addr, crawlerHeader=crawlerHeader, ip6Header=ip6Header)
        if retCode == 1 or retCode == 3:
            hubsAddrv4 = ips[0]  # Hubs / Ultrapeers
            leavesAddrv4 = ips[1]  # Leaves
        elif retCode == -1:
            continue
        else:
            print(f"Error while pinging {target_addr}: {retCode}\n")
            continue
        hubsAddrv6 = []  # temp fix while addresses are not split into ipv4 and ipv6 files
        leavesAddrv6 = []
        try:
            writeQueue_hubs.join()  # wait until all addresses in the writeQueue are processed to avoid duplicate writes... Seems buggy though, so checking again in writeToFile()
            writeQueue_leaves.join()
            with open(v4File_hubs, 'r+') as f:
                for addrTuple in hubsAddrv4:
                    if addrTuple[0] in f.read():
                        break
                    if _config.gnutella_sending_ipVer == 4:
                        if addrQueue.qsize() < _config.gnutella_addr_queue_size:
                            addrQueue.put(addrTuple)
                    if writeQueue_hubs.qsize() < _config.gnutella_write_queue_size:
                        writeQueue_hubs.put(('ipv4', addrTuple[0]))
                    else:
                        print("!! Write Queue full! Omitting IPv4-Addresses! !!")
            with open(v4File_leaves, 'r+') as f:
                for addrTuple in leavesAddrv4:
                    if addrTuple[0] in f.read():
                        break
                    if writeQueue_leaves.qsize() < _config.gnutella_write_queue_size:
                        writeQueue_leaves.put(('ipv4', addrTuple[0]))
                    else:
                        print("!! Write Queue full! Omitting IPv4-Addresses! !!")
            with open(v6File_hubs, 'r+') as f:
                for addrTuple in hubsAddrv6:
                    if addrTuple[0] in f.read():
                        break
                    if _config.gnutella_sending_ipVer == 6:
                        if addrQueue.qsize() < _config.gnutella_addr_queue_size:
                            addrQueue.put(addrTuple)
                            # print("Put in addrQueue")  # verbose
                    if writeQueue_hubs.qsize() < _config.gnutella_write_queue_size:
                        writeQueue_hubs.put(('ipv6', addrTuple[0]))
                        # print("Put in writeQueue")  # verbose
                    else:
                        print("!! Write Queue full! Omitting IPv6-Addresses! !!")
            with open(v6File_leaves, 'r+') as f:
                for addrTuple in leavesAddrv6:
                    if addrTuple[0] in f.read():
                        break
                    if writeQueue_leaves.qsize() < _config.gnutella_write_queue_size:
                        writeQueue_leaves.put(('ipv6', addrTuple[0]))
                    else:
                        print("!! Write Queue full! Omitting IPv6-Addresses! !!")
        except Exception as e:
            print(f"Error while writing to file: {e}\n")

        if fromQueue:
            addrQueue.task_done()


# def get_workerThreads(staticHeaderValues, run_event, num_threads, addrQueue, writeQueue):
#     workers = []
#     for i in range(num_threads):
#         args = {'staticHeaderValues': staticHeaderValues, 'run_event': run_event, 'addrQueue': addrQueue,
#                 'writeQueue': writeQueue}
#         worker = Thread(target=crawlDHT, kwargs=args)
#         worker.daemon = True
#         workers.append(worker)
#     return workers


