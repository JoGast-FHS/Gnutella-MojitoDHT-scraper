import os
import random
import secrets
import socket
import time
from threading import Thread
from queue import Queue
import DHT_GnutellaHeader
import DHT_GnutellaMessage
import _utilities_
import _config
import _targets



def get_static_header_blueprint():  # Gerüst ohne dynamische properties wie opcode, lokale KUID etc... Außerdem erst dictionary, was dann zum GnutellaHeader instanziieren genutzt wird
    message_id = str(secrets.token_hex(16))
    fdht_message = "44"
    version_major = "00"
    version_minor = "00"
    vendor = "54455354"  # 54 45 53 45 = "TEST", sonst z.B. "GTKG" (gtk-gnutella)
    contact_version_major = "00"
    contact_version_minor = "00"
    instance_id = "01"  # ?
    flags = "03"  # SHUTDOWN=1, Firewalled=1 -> 0b11 = 0x03
    extended_len = "0000"  # ?

    headerArguments = {
        'msgId': message_id,
        'fdhtMsg': fdht_message,
        'verMajor': version_major,
        'verMinor': version_minor,
        'payloadLen': "",
        'opcode': "",
        'vendor': vendor,
        'cVerMajor': contact_version_major,
        'cVerMinor': contact_version_minor,
        'kuid': "",
        'ipVer': "",
        'ipAddr': "",
        'ipPort': "",
        'instanceId': instance_id,
        'flags': flags,
        'extLength': extended_len,
    }
    return headerArguments


def get_headerConstants():
    localIP = _utilities_.get_local_ip(_config.dht_sending_ipVer)  # Unschön.. aber sonst muss bei jeder Iteration neu IP rausgefunden werden, inkl. Verbindungsaufbau... auch nicht gut
    publicIP = _utilities_.get_public_ip(_config.dht_ip_version)
    kuid = str(secrets.token_hex(20))  # zufällig generierte KUID (160bit laut doku) (lokale KUID)

    staticHeaderValues = {
        #statisch für gesamte Laufzeit
        'sending_ip_ver': _config.dht_sending_ipVer,
        'kuid': kuid,
        'ip_ver': _config.dht_ip_version,
        'local_ip': localIP,
        'public_ip': publicIP,
    }
    return staticHeaderValues


def findNode_Requests(staticHeaderValues, target, numRequests):
    if staticHeaderValues['sending_ip_ver'] == 4:
        addrFamily = socket.AF_INET
    else:
        addrFamily = socket.AF_INET6
    sock = socket.socket(addrFamily, socket.SOCK_DGRAM)
    sock.settimeout(_config.dht_socket_timeout)  # Socket schließt nach 20s
    sock.bind((staticHeaderValues['local_ip'], 0))

    payload_len = payload_len = f'{hex(58)[2:]}000000'  # Standard für FIND NODE REQUEST: 58 dec, 3a 00 00 00 (big endian)
    opcode = "05"  # FIND NODE REQUEST (5), FIND NODE REPLY (6), ...
    if staticHeaderValues['ip_ver'] == 4:
        ip_version = "04"
    else:
        ip_version = str(hex(16))[2:]  # ipv6: 0d16 -> 0x10
    ip_addr = _utilities_.ip2hex(staticHeaderValues['public_ip'], staticHeaderValues['ip_ver'])  # evt. auf IPv6 prüfen.. geht auch mit tunnelbroker?
    ip_port = hex(sock.getsockname()[1])[2:]  # lokal

    headerArgs = get_static_header_blueprint()
    # FIND NODE REQUEST spezifisch
    headerArgs['payloadLen'] = payload_len
    headerArgs['opcode'] = opcode

    # Verbindungsspezifisch
    headerArgs['ipPort'] = ip_port

    # Sessionspezifisch (statisch)
    headerArgs['kuid'] = staticHeaderValues['kuid']
    headerArgs['ipVer'] = ip_version
    headerArgs['ipAddr'] = ip_addr

    gnutella_header = DHT_GnutellaHeader.GnutellaHeader.fromArgs(headerArgs)

    for i in range(numRequests):
        target_kuid = secrets.token_hex(20)  # neue KUID zufällig generieren
        mojito_msg = bytearray.fromhex(gnutella_header.to_hexstr() + target_kuid)
        sock.sendto(mojito_msg, target)
    #print(f"{target} x{numRequests}")  # verbose

    recvAddrv4_list, recvAddrv6_list = recvReply(sock)
    if len(recvAddrv6_list) > 0:  # verbose
        print(f"Recv IPv6: {recvAddrv6_list}")
    sock.close()

    return recvAddrv4_list, recvAddrv6_list


def recvReply(sock):
    ipv4_addrList = []
    ipv6_addrList = []
    try:
        while True:
            data, sender_ip = sock.recvfrom(1024)  # buffer size is 1024 bytes
            message = DHT_GnutellaMessage.GnutellaMessage(data.hex())
            try:
                ipv4_addrList.extend(zip(message.ipv4_addresses_found, message.ipv4_ports_found))  # creating tuples
                ipv6_addrList.extend(zip(message.ipv6_addresses_found, message.ipv6_ports_found))
            except Exception:
                return [], []
            #print(message)
    except socket.timeout:
        #print("socket timeout")  # verbose
        print("Peer scanned.")
    return ipv4_addrList, ipv6_addrList


def initAddrQueue(staticHeaderValues, ip_ver):
    if _config.dht_sending_ipVer == 4:
        mojito_targets = _targets.dht_targets_ipv4
        os.makedirs(os.path.dirname(_config.dht_ipv4_file__ipv4Mode), exist_ok=True)  # create directories
        os.makedirs(os.path.dirname(_config.dht_ipv6_file__ipv4Mode), exist_ok=True)
        f4 = open(_config.dht_ipv4_file__ipv4Mode, 'w+')  # create files here, fix to issue that sometimes files were not created when crawler threads tried to open them
        f4.close()
        f6 = open(_config.dht_ipv6_file__ipv4Mode, 'w+')
        f6.close()
    else:
        mojito_targets = _targets.dht_targets_ipv6
        os.makedirs(os.path.dirname(_config.dht_ipv4_file__ipv6Mode), exist_ok=True)  # create directories
        os.makedirs(os.path.dirname(_config.dht_ipv6_file__ipv6Mode), exist_ok=True)
        f4 = open(_config.dht_ipv4_file__ipv6Mode, 'w+')  # create files here, fix to issue that sometimes files were not created when crawler threads tried to open them
        f4.close()
        f6 = open(_config.dht_ipv6_file__ipv6Mode, 'w+')
        f6.close()

    queue = Queue(maxsize=_config.dht_queue_size)
    for i in range(len(mojito_targets)):
        recvAddrv4, recvAddrv6 = findNode_Requests(staticHeaderValues=staticHeaderValues, target=mojito_targets[i], numRequests=_config.dht_number_of_requests_per_address)
        if ip_ver == 4:
            for addrTuple in recvAddrv4:
                if queue.qsize() < _config.dht_queue_size:
                    queue.put(addrTuple)
                else:
                    break
        else:
            for addrTuple in recvAddrv6:
                if queue.qsize() < _config.dht_queue_size:
                    queue.put(addrTuple)
                else:
                    break
    print("Queue initialized.")
    return queue


def crawlDHT(staticHeaderValues, run_event, addrQueue, writeQueue):
    if _config.dht_sending_ipVer == 4:
        v4File = _config.dht_ipv4_file__ipv4Mode
        v6File = _config.dht_ipv6_file__ipv4Mode
    else:
        v4File = _config.dht_ipv4_file__ipv6Mode
        v6File = _config.dht_ipv6_file__ipv6Mode

    while run_event.is_set():
        fromQueue = False
        if addrQueue.empty():  # fallback to hardcoded addresses
            if _config.dht_sending_ipVer == 4:
                addrNum = random.randint(0, (len(_targets.dht_targets_ipv4)-1))  # choose random addr from hardcoded ipv4 addr
                target_addr = _targets.dht_targets_ipv4[addrNum]
                print("Address queue empty - probably all IPv4 addresses scraped...")
            else:
                addrNum = random.randint(0, (len(_targets.dht_targets_ipv6)-1))  # choose random addr from hardcoded ipv6 addr
                target_addr = _targets.dht_targets_ipv6[addrNum]
                print("Address queue empty - probably no IPv6 addresses scraped or wrong configuration...")
        else:
            target_addr = addrQueue.get()
            fromQueue = True

        recvAddrv4, recvAddrv6 = findNode_Requests(staticHeaderValues=staticHeaderValues, target=target_addr, numRequests=_config.dht_number_of_requests_per_address)
        writeQueue.join()  # wait until all addresses in the writeQueue are processed to avoid duplicate writes... Seems buggy though, so checking again in writeToFile()
        with open(v4File, 'r+') as f:
            for addrTuple in recvAddrv4:
                if addrTuple[0] in f.read():
                    break
                if _config.dht_sending_ipVer == 4:
                    if addrQueue.qsize() < _config.dht_queue_size:
                        addrQueue.put(addrTuple)
                if writeQueue.qsize() < _config.dht_write_queue_size:
                    writeQueue.put(('ipv4', addrTuple[0]))
                else:
                    print("Write Queue full! Omitting IPv4-Addresses!!!")
        with open(v6File, 'r+') as f:
            for addrTuple in recvAddrv6:
                if addrTuple[0] in f.read():
                    break
                if _config.dht_sending_ipVer == 6:
                    if addrQueue.qsize() < _config.dht_queue_size:
                        addrQueue.put(addrTuple)
                        print("Put in addrQueue")  # verbose
                if writeQueue.qsize() < _config.dht_write_queue_size:
                    writeQueue.put(('ipv6', addrTuple[0]))
                    print("Put in writeQueue")  # verbose
                else:
                    print("Write Queue full! Omitting IPv6-Addresses!!!")
        if fromQueue:
            addrQueue.task_done()


def get_workerThreads(staticHeaderValues, run_event, num_threads, addrQueue, writeQueue):
    workers = []
    for i in range(num_threads):
        args = {'staticHeaderValues': staticHeaderValues, 'run_event': run_event, 'addrQueue': addrQueue, 'writeQueue': writeQueue}
        worker = Thread(target=crawlDHT, kwargs=args)
        worker.daemon = True
        workers.append(worker)
    return workers


def writeToFile(writeQueue, run_event, filenamev4, filenamev6):
    f4 = open(filenamev4, 'a+')  # make sure files are created
    f4.close()
    f6 = open(filenamev6, 'a+')
    f6.close()

    while run_event.is_set():
        while not writeQueue.empty():
            version, addr = writeQueue.get()
            if version == 'ipv4':
                with open(filenamev4, 'r+') as f:  # open as read so cursor starts at beginning of file
                    if addr not in f.read():
                        f.write(addr + "\n")
            else:
                with open(filenamev6, 'r+') as f:
                    if addr not in f.read():
                        f.write(addr + "\n")
                        print("Wrote to file")  # verbose
            writeQueue.task_done()
        time.sleep(3)


def get_writerThread(writeQueue, run_event):
    if _config.dht_sending_ipVer == 4:
        v4File = _config.dht_ipv4_file__ipv4Mode
        v6File = _config.dht_ipv6_file__ipv4Mode
    else:
        v4File = _config.dht_ipv4_file__ipv6Mode
        v6File = _config.dht_ipv6_file__ipv6Mode
    args = {'writeQueue': writeQueue, 'run_event': run_event, 'filenamev4': v4File, 'filenamev6': v6File}
    writer = Thread(target=writeToFile, kwargs=args)
    writer.daemon = True
    return writer


def runThreads(workers, writer, run_event):
    for w in workers:
        w.start()
    writer.start()

    try:
        while True:
            time.sleep(.5)
    except KeyboardInterrupt:
        print("Stopping workers...")
        run_event.clear()
        for w in workers:
            w.join()
        writer.join()
        print("Workers stopped. Exiting.")


