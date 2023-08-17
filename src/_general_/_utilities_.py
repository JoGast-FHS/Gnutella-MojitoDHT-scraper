# Utility functions used by dht and gnutella messaging

import ipaddress
import json
import time

import requests
import socket
import threading

from config import _config


def get_public_ip(ip_ver):
    try:
        response = requests.get(f"https://api{ip_ver}.ipify.org?format=json")  # ipv4 addr or ipv6 addr
        json_response = json.loads(response.text)
        publicIP = json_response['ip']
    except requests.exceptions:
        print("Time out getting public IP-Address. Possibly running in IPv6 mode with no IPv6 connection, or ipify.org API not reachable.")
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
    addr_bytearray = bytearray.fromhex(ip_addr)
    if ip_ver == 4:
        addr_family = socket.AF_INET
    else:
        addr_family = socket.AF_INET6
        print(ip_addr)
    return socket.inet_ntop(addr_family, addr_bytearray)


def get_Filenames(crawler):
    if crawler == "gnutella":
        if _config.gnutella_sending_ipVer == 4:
            v4File_hubs_crawler = _config.gnutella_ipv4_file_hubs_Crawler
            v4File_leaves_crawler = _config.gnutella_ipv4_file_leaves_Crawler
            v6File_hubs_crawler = _config.gnutella_ipv6_file_hubs_Crawler
            v6File_leaves_crawler = _config.gnutella_ipv6_file_leaves_Crawler
            v4File_hubs_ping = _config.gnutella_ipv4_file_hubs_Ping
            v4File_leaves_ping = _config.gnutella_ipv4_file_leaves_Ping
            v6File_hubs_ping = _config.gnutella_ipv6_file_hubs_Ping
            v6File_leaves_ping = _config.gnutella_ipv6_file_leaves_Ping
        else:   # not used atm
            v4File_hubs_crawler = _config.gnutella_ipv4_file_hubs_Crawler
            v4File_leaves_crawler = _config.gnutella_ipv4_file_leaves_Crawler
            v6File_hubs_crawler = _config.gnutella_ipv6_file_hubs_Crawler
            v6File_leaves_crawler = _config.gnutella_ipv6_file_leaves_Crawler
            v4File_hubs_ping = _config.gnutella_ipv4_file_hubs_Ping
            v4File_leaves_ping = _config.gnutella_ipv4_file_leaves_Ping
            v6File_hubs_ping = _config.gnutella_ipv6_file_hubs_Ping
            v6File_leaves_ping = _config.gnutella_ipv6_file_leaves_Ping
        return v4File_hubs_crawler, v4File_leaves_crawler, v6File_hubs_crawler, v6File_leaves_crawler, v4File_hubs_ping, v4File_leaves_ping, v6File_hubs_ping, v6File_leaves_ping
    elif crawler == "mojito":
        if _config.dht_sending_ipVer == 4:
            v4File = _config.dht_ipv4_file__ipv4Mode
            v6File = _config.dht_ipv6_file__ipv4Mode
        else:
            v4File = _config.dht_ipv4_file__ipv6Mode
            v6File = _config.dht_ipv6_file__ipv6Mode
        return v4File, v6File
    else:
        return "Cannot get filenames for unknown crawler."


def replaceStr(str, index, newStr):
    return str[:index] + newStr + str[index + len(newStr):]


def get_workerThreads(target, run_event, num_threads, addrQueue, writeQueues, staticHeaderValues):
    workers = []
    for i in range(num_threads):
        if staticHeaderValues == "":
            args = {'run_event': run_event, 'addrQueue': addrQueue, 'writeQueues': writeQueues}
        else:
            args = {'staticHeaderValues': staticHeaderValues, 'run_event': run_event, 'addrQueue': addrQueue, 'writeQueues': writeQueues}
        worker = threading.Thread(target=target, kwargs=args)
        worker.daemon = True
        workers.append(worker)
    return workers


def writeToFile(writeQueue, run_event, v4File, v6File):
    f4 = open(v4File, 'a+')  # make sure files are created
    f4.close()
    f6 = open(v6File, 'a+')
    f6.close()

    while run_event.is_set():
        while not writeQueue.empty():
            version, addr = writeQueue.get()
            if version == 'ipv4':
                with open(v4File, 'r+') as f:  # open as read so cursor starts at beginning of file
                    if addr not in f.read():
                        f.write(addr + "\n")
            else:
                with open(v6File, 'r+') as f:
                    if addr not in f.read():
                        f.write(addr + "\n")
                        #print("Wrote to file")  # verbose
            writeQueue.task_done()
        time.sleep(2)


def get_writerThread(writeQueues, run_event):
    if _config.crawler == "gnutella":
        v4File_hubs_c, v4File_leaves_c, v6File_hubs_c, v6File_leaves_c, v4File_hubs_p, v4File_leaves_p, v6File_hubs_p, v6File_leaves_p = get_Filenames("gnutella")
        if _config.gnutella_crawlerHeader:
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
        argsHubs = {'writeQueue': writeQueue_hubs, 'run_event': run_event, 'v4File': v4File_hubs, 'v6File': v6File_hubs}
        argsLeaves = {'writeQueue': writeQueue_leaves, 'run_event': run_event, 'v4File': v4File_leaves, 'v6File': v6File_leaves}
        hubWriter = threading.Thread(target=writeToFile, kwargs=argsHubs)
        leafWriter = threading.Thread(target=writeToFile, kwargs=argsLeaves)
        writers = [leafWriter, hubWriter]
    else:
        v4File, v6File = get_Filenames("mojito")
        writeQueue = writeQueues[0]
        args = {'writeQueue': writeQueue, 'run_event': run_event, 'v4File': v4File, 'v6File': v6File}
        writer = threading.Thread(target=writeToFile, kwargs=args)
        writers = [writer]

    for writer in writers:
        writer.daemon = True
    return writers


def runThreads(workers, writers, run_event):
    for worker in workers:
        worker.start()
    for writer in writers:
        writer.start()

    try:
        while True:
            time.sleep(.5)
    except KeyboardInterrupt:
        print("-----------------------------------\nStopping workers...")
        run_event.clear()
        for w in workers:
            w.join()
        for writer in writers:
            writer.join()
        print("Workers stopped. Exiting.")