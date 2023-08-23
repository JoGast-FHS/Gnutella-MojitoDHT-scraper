import random
import socket
import threading
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


def decompressHexstring(hexstr):
    decompressor = zlib.decompressobj()
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
    return decompressed_hexstring, decompressed_bytestr


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
            print(f"503 - Got Peer-IPs: {hubIPs}")
        if 'Leaves' in gnutellaResponse.headers:
            tryIPs = gnutellaResponse.headers['Leaves'].replace(' ', '').replace('\r\n', '').split(',')
            for ip in tryIPs:
                ipTuple = ip.split(':')
                leafIPs.append((ipTuple[0], int(ipTuple[1].split(' ')[0])))
            print(f"503 - Got Leaf-IPs: {leafIPs}\n")
    else:
         print(f"Unknown banner: < {gnutellaResponse.banner} >\n")
         return 2, []
    return 1, [hubIPs, leafIPs]


def doHandshake(sock, target, crawlerHeader=False, ip6Header=False, noACK=False):
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
            if 'X-Ultrapeer' in gnutellaResponse.headers:
                if gnutellaResponse.headers['X-Ultrapeer'] == "True":
                    return 0, 1
                elif gnutellaResponse.headers['X-Ultrapeer'] == "False":
                    return 0, 0
            else:
                return 0, -1
        else:
            return processGnutellaError(gnutellaResponse, foundIPs)


'''
    Checks if G1/G2 Peer is an Ultrapeer or a Leaf/undetermined
'''
def isUltrapeer(ipTuple):
    sock = createGnutellaSocket()
    sock.connect(ipTuple)
    handshakeResp = doHandshake(sock=sock, target=ipTuple, crawlerHeader=False, ip6Header=False, noACK=True)
    if handshakeResp[0] == 0:
        ultrapeer = handshakeResp[1]
        if ultrapeer == 1:
            print(f"{ipTuple[0]} is Ultrapeer\n")  # verbose
        elif ultrapeer == 0:
            print(f"{ipTuple[0]} is Leaf\n")  # verbose
        else:
            print(f"{ipTuple[0]} is ??? (no header)\n")  # verbose
        return ultrapeer
    return -2


def processExtensionBlock(extBlock):
    pass


def processPong(pongPacket, checkUP=True):
    ips = []
    ips.append([])  # hubIPs
    ips.append([])  # leafIPs
    if pongPacket.payloadtype == "01" and pongPacket.payloadlen != 0:  # if Pong
        tmp_packet = pongPacket
        while True:
            payload_remainder, ipTuple = tmp_packet.processPayload()
            ultrapeer = 0
            try:
                if checkUP:
                    inUfile = False
                    inLfile = False
                    _, _, _, _, v4File_hubs_p, v4File_leaves_p, _, _ = _utilities_.get_Filenames("gnutella")
                    with _utilities_.queues_lock:
                        with open(v4File_hubs_p, 'r+') as f:  # check only if IP is not already in one of the files
                            if ipTuple[0] in f.read():
                                inUfile = True
                            f.close()
                        if not inUfile:
                            with open(v4File_leaves_p, 'r+') as f:
                                if ipTuple[0] in f.read():
                                    inLfile = True
                                f.close()
                    if inUfile:
                        ultrapeer = 1
                        print("-> Hub already known-")  # verbose
                    elif inLfile:
                        ultrapeer = 0
                        print("-> Leaf already known")  # verbose
                    else:
                        ultrapeer = isUltrapeer(ipTuple)  # ^ see last comment
            except KeyError as e:
                print(f"KeyError getting peer status: {e}\n")  # verbose
            except Exception as e:
                print(f"Exception thrown getting peer status: {e}\n")  # verbose
            if ultrapeer == 1:
                ips[0].append(ipTuple)
            else:
                ips[1].append(ipTuple)  # note: also peers where status is undetermined are added to leaves!
            tmp_packet = Gnutella_GnutellaPacket.GnutellaPacket.fromString(payload_remainder)
            if payload_remainder == "":  # once payload has been fully processed
                print("\n")
                return 3, ips
    else:
        print("Received something other than a Pong - no further processing.")
        return -1, []


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
        handshakeResp = doHandshake(sock, target, crawlerHeader, ip6Header)
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
                    recv_bytes = sock.recv(1024*2)
                    hexstr = recv_bytes.hex()
                    decompressed_hexstring, decompressed_bytestring = decompressHexstring(hexstr)
                    # print(f"Orig. Hexstr: {hexstr}")  # verbose
                    # print(f"Pong decompressed: {decompressed_hexstring}")  # verbose
                    pongPacket = Gnutella_GnutellaPacket.GnutellaPacket.fromString(decompressed_hexstring)
                    retCode, ips = processPong(pongPacket)
                    if retCode == 3:
                        return retCode, ips
                    else:
                        continue
            except zlib.error:
                print(f"Error compressing/decompressing: zlib Error thrown\n")

    except socket.timeout:
        print(f"Error while pinging {target}: Timeout\n")
    except ConnectionError:
        print(f"Error while pinging {target}: Connection failed\n")
    except UnicodeDecodeError:
        print(f"Error while decoding response from {target}\n")
    except KeyError:
        #raise  # debugging purposes
        print(f"Error while pinging {target}: KeyError\n")
    except AttributeError:
        print(f"Error while pinging {target}: Message initialization failed (known issue)\n")
    except Exception as e:
        print(f"Unknown error while pinging {target}: {e}\n")
    return ret


def gnutellaPings(target, crawlerHeader=False, ip6Header=False):
    sock = createGnutellaSocket()
    try:
        sockName = sock.getsockname()[0]
        sockPort = sock.getsockname()[1]
        print(f"{sockName}:{sockPort} --> {target[0]}:{target[1]}")  # verbose
        retCode, retIPs = ping(sock, target, crawlerHeader, ip6Header)
    except IndexError:
        pass
    sock.close()
    return retCode, retIPs


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

    emptyTries = 0
    while run_event.is_set():
        fromQueue = False
        if addrQueue.empty():  # fallback to hardcoded addresses
            emptyTries += 1
            if emptyTries >= 5:
                run_event.clear()
                return
            if _config.gnutella_sending_ipVer == 4:
                addrNum = random.randint(0, (len(_targets.gnutella_targets_ipv4) - 1))  # choose random addr from hardcoded ipv4 addr
                target_addr = _targets.gnutella_targets_ipv4[addrNum]
                print("Address queue empty - probably all IPv4 addresses in Gnutella networks crawled, using only ultrapeers as seeds or using unreachable seed nodes (-> seed manually)...")
            else:
                addrNum = random.randint(0, (len(_targets.gnutella_targets_ipv6) - 1))  # choose random addr from hardcoded ipv6 addr
                target_addr = _targets.gnutella_targets_ipv6[addrNum]
                print("Address queue empty - probably no IPv6 addresses scraped or wrong configuration...")
        else:
            with _utilities_.queues_lock:
                target_addr = addrQueue.get()
                addrQueue.task_done()
            fromQueue = True
        with _utilities_.queues_lock:
            if target_addr == None or target_addr == "" or target_addr == [] or type(target_addr) is not tuple:  # last condition: Weird bug that was encountered rarely would push entire hanshake packet into queue byte by byte
                print("Error: Failed to initialize target address.\n")  # verbose
                continue
            elif target_addr in _utilities_.faultyAddrSet:
                continue
            elif target_addr in _utilities_.allAddrSet:
                continue

        retCode, ips = gnutellaPings(target=target_addr, crawlerHeader=crawlerHeader, ip6Header=ip6Header)
        # print(f"retCode is {retCode}, type is {type(retCode)}")  # debugging
        if retCode == 1 or retCode == 3:
            # print("Inside 'IF' (1 or 3)\n")  # debugging
            hubsAddrv4 = ips[0]  # Hubs / Ultrapeers
            leavesAddrv4 = ips[1]  # Leaves
        # elif retCode == -1:
        #     # print("Inside 'ELIF' (-1)\n")  # debugging
        #     with _utilities_.queues_lock:
        #         if target_addr not in _utilities_.faultyAddrSet:
        #             _utilities_.faultyAddrSet.add(target_addr)
        #             hubsAddrv4 = [target_addr]
        #             leavesAddrv4 = []
        #         else:
        #             continue
        else:
            # print("Inside 'ELSE'\n")  # debugging
            if retCode != -1:
                print(f"Error while pinging {target_addr}: {retCode}\n")  # verbose
            with _utilities_.queues_lock:
                if target_addr not in _utilities_.faultyAddrSet:
                    _utilities_.faultyAddrSet.add(target_addr)
                    hubsAddrv4 = [target_addr]
                    leavesAddrv4 = []
                else:
                    continue
        hubsAddrv6 = []  # temp fix while addresses are not split into ipv4 and ipv6 files
        leavesAddrv6 = []
        try:
            # writeQueue_hubs.join()  # wait until all addresses in the writeQueue are processed to avoid duplicate writes... Seems buggy though, so checking again in writeToFile()
            # writeQueue_leaves.join()
            with _utilities_.queues_lock:
                with open(v4File_hubs, 'r+') as f:
                    for addrTuple in hubsAddrv4:
                        if type(addrTuple) is not tuple:
                            continue
                        elif addrTuple in _utilities_.allAddrSet or addrTuple in addrQueue.queue:  # !! direct queue access possibly not thread safe... may require further testing
                            continue
                        # elif addrTuple[0] in f.read():  # not used for now because we want to catch hubs on all open ports
                        #     continue
                        elif _config.gnutella_sending_ipVer == 4:
                            if addrQueue.qsize() < _config.gnutella_addr_queue_size:
                                addrQueue.put(addrTuple)
                        if ('ipv4', addrTuple) in writeQueue_leaves.queue or ('ipv4', addrTuple) in writeQueue_hubs.queue:
                            continue
                        elif writeQueue_hubs.qsize() < _config.gnutella_write_queue_size:
                            writeQueue_hubs.put(('ipv4', addrTuple))
                        else:
                            print("!! Write Queue full! Omitting IPv4-Addresses! !!")
                with open(v4File_leaves, 'r+') as f:
                    for addrTuple in leavesAddrv4:
                        if type(addrTuple) is not tuple:
                            continue
                        elif addrTuple in _utilities_.allAddrSet or addrTuple in addrQueue.queue or (
                                'ipv4', addrTuple) in writeQueue_leaves.queue or (
                                'ipv4', addrTuple) in writeQueue_hubs.queue:
                            continue
                        # elif addrTuple[0] in f.read():
                        #     continue
                        elif writeQueue_leaves.qsize() < _config.gnutella_write_queue_size:
                            writeQueue_leaves.put(('ipv4', addrTuple))
                        else:
                            print("!! Write Queue full! Omitting IPv4-Addresses! !!")
                with open(v6File_hubs, 'r+') as f:
                    for addrTuple in hubsAddrv6:
                        if type(addrTuple) is not tuple:
                            continue
                        elif addrTuple in _utilities_.allAddrSet or addrTuple in addrQueue.queue:
                            continue
                        # elif addrTuple[0] in f.read():
                        #     continue
                        elif _config.gnutella_sending_ipVer == 6:
                            if addrQueue.qsize() < _config.gnutella_addr_queue_size:
                                addrQueue.put(addrTuple)
                                # print("Put in addrQueue")  # verbose
                        if ('ipv6', addrTuple) in writeQueue_leaves.queue or ('ipv6', addrTuple) in writeQueue_hubs.queue:
                            continue
                        elif writeQueue_hubs.qsize() < _config.gnutella_write_queue_size:
                            writeQueue_hubs.put(('ipv6', addrTuple))
                            # print("Put in writeQueue")  # verbose
                        else:
                            print("!! Write Queue full! Omitting IPv6-Addresses! !!")
                with open(v6File_leaves, 'r+') as f:
                    for addrTuple in leavesAddrv6:
                        if type(addrTuple) is not tuple:
                            continue
                        elif addrTuple in _utilities_.allAddrSet or addrTuple in addrQueue.queue or (
                                'ipv6', addrTuple) in writeQueue_leaves.queue or (
                                'ipv6', addrTuple) in writeQueue_hubs.queue:
                            continue
                        # elif addrTuple[0] in f.read():
                        #     continue
                        elif writeQueue_leaves.qsize() < _config.gnutella_write_queue_size:
                            writeQueue_leaves.put(('ipv6', addrTuple))
                        else:
                            print("!! Write Queue full! Omitting IPv6-Addresses! !!")
        except Exception as e:
            print(f"Error while writing to file: {e}\n")

        # if fromQueue:
        #     addrQueue.task_done()


# def get_workerThreads(staticHeaderValues, run_event, num_threads, addrQueue, writeQueue):
#     workers = []
#     for i in range(num_threads):
#         args = {'staticHeaderValues': staticHeaderValues, 'run_event': run_event, 'addrQueue': addrQueue,
#                 'writeQueue': writeQueue}
#         worker = Thread(target=crawlDHT, kwargs=args)
#         worker.daemon = True
#         workers.append(worker)
#     return workers


