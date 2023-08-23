# This file contains functions that use both the Gnutella and the Mojito DHT utilities.
import os
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
