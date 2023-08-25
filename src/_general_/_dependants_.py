# This file contains functions that use both the Gnutella and the Mojito DHT utilities.
import os
import random
from queue import Queue

from src.MojitoDHT import DHT_utilities
from src.Gnutella import Gnutella_utilities
from src._general_ import _utilities_
from config import _config
from config import _targets


def initAddrQueue(addrQSize, staticHeaderValues, ip_ver):
    if _config.crawler == "mojito":
        gnutella = False
        numRequests = _config.dht_num_requests
        v4File_DHT, v6File_DHT = _utilities_.get_Filenames("mojito")
        with _utilities_.queues_lock:
            os.makedirs(os.path.dirname(v4File_DHT), exist_ok=True)  # create directories
            os.makedirs(os.path.dirname(v6File_DHT), exist_ok=True)
            f4 = open(v4File_DHT, 'w+')  # create files here, bandaid fix to issue that sometimes files were not created when crawler threads tried to open them
            f4.close()
            f6 = open(v6File_DHT, 'w+')
            f6.close()
        if _config.dht_sending_ipVer == 4:
            targets = _targets.dht_targets_ipv4
        else:
            targets = _targets.dht_targets_ipv6
    elif _config.crawler == "gnutella":
        gnutella = True
        numRequests = _config.gnutella_num_requests
        targets = _targets.gnutella_targets_ipv4
        v4File_hubs_c, v4File_leaves_c, v6File_hubs_c, v6File_leaves_c, v4File_hubs_p, v4File_leaves_p, v6File_hubs_p, v6File_leaves_p = _utilities_.get_Filenames("gnutella")
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
        with _utilities_.queues_lock:
            os.makedirs(os.path.dirname(v4File_hubs), exist_ok=True)  # create directories
            os.makedirs(os.path.dirname(v6File_hubs), exist_ok=True)
            os.makedirs(os.path.dirname(v4File_leaves), exist_ok=True)
            os.makedirs(os.path.dirname(v6File_leaves), exist_ok=True)
            with open(v4File_hubs, 'w') as f:  # create files here, bandaid fix to issue that sometimes files were not created when crawler threads tried to open them
                pass
            with open(v6File_hubs, 'w') as f:
                pass
            with open(v4File_leaves, 'w') as f:
                pass
            with open(v6File_leaves, 'w') as f:
                pass
    else:
        print("Error: No valid crawler specified in config.py!")
        exit(1)

    queue = Queue(maxsize=addrQSize)
    for i in range(len(targets)):
        if gnutella:
            retCode, ips = Gnutella_utilities.gnutellaPings(target=targets[i], crawlerHeader=_config.gnutella_crawlerHeader, ip6Header=_config.gnutella_ip6Header)
            if retCode == 1 or retCode == 3:
                recvAddrv4 = ips[0]
            else :
                recvAddrv4 = []
            recvAddrv6 = []  #temp fix while addresses are not split into ipv4 and ipv6 files
        else:
            recvAddrv4, recvAddrv6 = DHT_utilities.findNode_Requests(staticHeaderValues=staticHeaderValues, target=targets[i], numRequests=numRequests)
        if ip_ver == 4:
            for addrTuple in recvAddrv4:
                if queue.qsize() < addrQSize:
                    queue.put(addrTuple)
                else:
                    break
        else:
            for addrTuple in recvAddrv6:
                if queue.qsize() < addrQSize:
                    queue.put(addrTuple)
                else:
                    break
    print("\n---------------------- Queue initialized. ----------------------\n\n")
    return queue



def crawl(run_event, addrQueue, writeQueues, staticHeaderValues, ip6Header=False):
    if _config.crawler == "gnutella":
        crawlerHeader = _config.gnutella_crawlerHeader
        writeQueue_hubs = writeQueues[0]
        writeQueue_leaves = writeQueues[1]
        crawler_addrQSize = _config.gnutella_addr_queue_size
        crawler_writeQSize = _config.gnutella_write_queue_size
        nodeType = "Hub"
    elif _config.crawler == "mojito":
        writeQueue_hubs = writeQueues[0]  # only one type of peer in this mode
        writeQueue_leaves = writeQueues[0]
        crawler_addrQSize = _config.dht_addr_queue_size
        crawler_writeQSize = _config.dht_write_queue_size
        nodeType = "DHT-node"
    else:
        return

    emptyTries = 0
    while run_event.is_set():
        if addrQueue.empty():  # fallback to hardcoded addresses
            emptyTries += 1
            if emptyTries >= 5:
                run_event.clear()
                return
            if _config.crawler == "gnutella":
                if _config.gnutella_sending_ipVer == 4:
                    addrNum = random.randint(0, (len(_targets.gnutella_targets_ipv4) - 1))  # choose random addr from hardcoded ipv4 addr
                    target_addr = _targets.gnutella_targets_ipv4[addrNum]
                    print("Address queue empty - probably all IPv4 addresses in Gnutella networks crawled, using only ultrapeers as seeds or using unreachable seed nodes (-> seed manually)...")
                else:
                    addrNum = random.randint(0, (len(_targets.gnutella_targets_ipv6) - 1))  # choose random addr from hardcoded ipv6 addr
                    target_addr = _targets.gnutella_targets_ipv6[addrNum]
                    print("Address queue empty - probably no IPv6 addresses scraped or wrong configuration...")
            elif _config.crawler == "mojito":
                if _config.dht_sending_ipVer == 4:
                    addrNum = random.randint(0, (len(_targets.dht_targets_ipv4) - 1))  # choose random addr from hardcoded ipv4 addr
                    target_addr = _targets.dht_targets_ipv4[addrNum]
                    print("Address queue empty - probably all IPv4 addresses in DHT scraped or using unreachable seed "
                          "nodes (-> seed manually)...")
                else:
                    addrNum = random.randint(0, (len(_targets.dht_targets_ipv6) - 1))  # choose random addr from hardcoded ipv6 addr
                    target_addr = _targets.dht_targets_ipv6[addrNum]
                    print("Address queue empty - probably no IPv6 addresses scraped or wrong configuration...")
            else:
                return
        else:
            with _utilities_.queues_lock:
                target_addr = addrQueue.get()
                addrQueue.task_done()
        with _utilities_.queues_lock:
            if target_addr == None or target_addr == "" or target_addr == [] or type(target_addr) is not tuple:  # last condition: Weird bug that was encountered rarely would push entire hanshake packet into queue byte by byte
                print("Error: Failed to initialize target address.\n")  # verbose
                continue
            elif target_addr in _utilities_.faultyAddrSet:
                continue

        undetermined = []
        if _config.crawler == "gnutella":
            retCode, ips = Gnutella_utilities.gnutellaPings(target=target_addr, crawlerHeader=crawlerHeader, ip6Header=ip6Header)
            if retCode == 1 or retCode == 3:
                hubsAddrv4 = ips[0]  # Hubs / Ultrapeers
                leavesAddrv4 = ips[1]  # Leaves
            elif retCode == 4:
                hubsAddrv4 = ips[0]  # Hubs / Ultrapeers
                leavesAddrv4 = ips[1]  # Leaves
                undetermined = ips[2]  # only case where peers of undetermined status need to be examined separately
            else:
                if retCode != -1:
                    print(f"Error while pinging {target_addr}: {retCode}\n")  # verbose
                with _utilities_.queues_lock:
                    if target_addr not in _utilities_.faultyAddrSet:
                        _utilities_.faultyAddrSet.add(target_addr)
                        hubsAddrv4 = []
                    else:
                        continue  # faulty addresses are processed once to ensure they are added to files
            hubsAddrv6 = []  # temp fix while addresses are not split into ipv4 and ipv6 files
            leavesAddrv6 = []
            hubsAddrv4.append(target_addr)
        elif _config.crawler == "mojito":
            try:
                hubsAddrv4, hubsAddrv6 = DHT_utilities.findNode_Requests(staticHeaderValues=staticHeaderValues, target=target_addr, numRequests=_config.dht_num_requests)
                if staticHeaderValues['sending_ip_ver'] == 4:
                    hubsAddrv4.append(target_addr)  # make sure that target address is also written down (e.g. if learned while initializing queue)
                else:
                    hubsAddrv6.append(target_addr)
            except:
                print(f"Failed to send requests to {target_addr}")
                continue
            leavesAddrv4 = []
            leavesAddrv6 = []
        else:
            return

        try:
            with _utilities_.queues_lock:
                for addrTuple in hubsAddrv4:
                    if type(addrTuple) is not tuple:
                        continue
                    elif (addrTuple not in addrQueue.queue) and (addrTuple not in _utilities_.pingedAddrSet) and (addrQueue.qsize() < crawler_addrQSize):
                        addrQueue.put(addrTuple)
                    if addrTuple in _utilities_.writtenAddrSet or _utilities_.inQueues(('ipv4', addrTuple), writeQueues):
                        print(f"--> IPv4 {nodeType} {addrTuple} skipped (already known)")  # verbose
                    else:
                        if (writeQueue_hubs.qsize() < crawler_writeQSize):
                            writeQueue_hubs.put(('ipv4', addrTuple))
                            print(f"--> IPv4 {nodeType} {addrTuple} saved")  # verbose
                        else:
                            print("!! Write Queue full! Omitting IPv4-Addresses! !!")

                for addrTuple in leavesAddrv4:
                    if type(addrTuple) is not tuple:
                        continue
                    elif addrTuple in _utilities_.writtenAddrSet or _utilities_.inQueues(('ipv4', addrTuple), writeQueues):
                        print(f"--> IPv4 Leaf {addrTuple} skipped (already known)")  # verbose
                        continue
                    if writeQueue_leaves.qsize() < crawler_writeQSize:
                        writeQueue_leaves.put(('ipv4', addrTuple))
                        print(f"--> IPv4 Leaf {addrTuple} saved")  # verbose
                    else:
                        print("!! Write Queue full! Omitting IPv4-Addresses! !!")

                for addrTuple in undetermined:
                    if type(addrTuple) is not tuple:
                        continue
                    elif (addrTuple not in addrQueue.queue) and (addrTuple not in _utilities_.pingedAddrSet) and (addrQueue.qsize() < crawler_addrQSize):
                        addrQueue.put(addrTuple)
                    if addrTuple in _utilities_.writtenAddrSet or _utilities_.inQueues(('ipv4', addrTuple), writeQueues):
                        print(f"--> Undetermined {addrTuple} skipped (already known)")  # verbose
                    else:
                        if (writeQueue_leaves.qsize() < crawler_writeQSize):
                            writeQueue_leaves.put(('ipv4', addrTuple))
                            print(f"--> Undetermined {addrTuple} saved")  # verbose
                        else:
                            print("!! Write Queue full! Omitting IPv4-Addresses! !!\n")

                for addrTuple in hubsAddrv6:
                    if type(addrTuple) is not tuple:
                        continue
                    elif (addrTuple not in addrQueue.queue) and (addrTuple not in _utilities_.pingedAddrSet) and (addrQueue.qsize() < crawler_addrQSize):
                        addrQueue.put(addrTuple)
                    if addrTuple in _utilities_.writtenAddrSet or _utilities_.inQueues(('ipv6', addrTuple), writeQueues):
                        print(f"--> IPv6 {nodeType} {addrTuple} skipped (already known)")  # verbose
                    else:
                        if (writeQueue_hubs.qsize() < crawler_writeQSize):
                            writeQueue_hubs.put(('ipv6', addrTuple))
                            print(f"--> IPv6 {nodeType} {addrTuple} saved")  # verbose
                        else:
                            print("!! Write Queue full! Omitting IPv6-Addresses! !!\n")

                for addrTuple in leavesAddrv6:
                    if type(addrTuple) is not tuple:
                        continue
                    elif addrTuple in _utilities_.writtenAddrSet or _utilities_.inQueues(('ipv6', addrTuple), writeQueues):
                        print(f"--> IPv6 Leaf {addrTuple} skipped (already known)")  # verbose
                        continue
                    if writeQueue_leaves.qsize() < crawler_writeQSize:
                        writeQueue_leaves.put(('ipv6', addrTuple))
                        print(f"--> IPv6 Leaf {addrTuple} saved")  # verbose
                    else:
                        print("!! Write Queue full! Omitting IPv6-Addresses! !!")

        except Exception as e:
            print(f"Error while writing to file: {e}\n")

        _utilities_.pingedAddrSet.add(target_addr)
