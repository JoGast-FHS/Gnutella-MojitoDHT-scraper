import zlib
from threading import Event
from queue import Queue

from config import _config
from src.MojitoDHT import DHT_utilities
from src.Gnutella import Gnutella_utilities
from src._general_ import _utilities_
from src._general_ import _dependants_



if __name__ == "__main__":

    if _config.crawler == "gnutella":
        staticHeaderValues = ""
        numThreads = _config.gnutella_num_worker_threads
        writeQSize = _config.gnutella_write_queue_size
        addrQSize = _config.gnutella_addr_queue_size
        ip_ver = 4
        targetFunction = Gnutella_utilities.crawlGnutella

    elif _config.crawler == "mojito":
        staticHeaderValues = DHT_utilities.get_headerConstants()
        numThreads = _config.dht_num_worker_threads
        writeQSize = _config.dht_write_queue_size
        addrQSize = _config.dht_addr_queue_size
        ip_ver = _config.dht_sending_ipVer
        targetFunction = DHT_utilities.crawlDHT


        # pingQ, writeQ = Gnutella_utilities.initGnutella(_config.gnutella_crawlerHeader, _config.gnutella_ip6Header)
        # Gnutella_utilities.crawlGnutella(pingQ, writeQ, _config.gnutella_crawlerHeader, _config.gnutella_ip6Header)



    # elif _config.crawler == "mojito":
    #     staticHeaderValues = DHT_utilities.get_headerConstants()
    #     addressQueue = DHT_utilities.initAddrQueue(staticHeaderValues=staticHeaderValues, ip_ver=_config.dht_sending_ipVer)
    #     writeQueue = Queue(maxsize=_config.dht_write_queue_size)
    #     run_event = Event()
    #     run_event.set()
    #
    #     workerThreads = DHT_utilities.get_workerThreads(run_event=run_event, num_threads=_config.dht_num_worker_threads, addrQueue=addressQueue, writeQueue=writeQueue, staticHeaderValues=staticHeaderValues)
    #     writerThread = DHT_utilities.get_writerThread(writeQueue=writeQueue, run_event=run_event)
    #     DHT_utilities.runThreads(workerThreads, writerThread, run_event)

        # 1) initial requests to populate queue
        # 2) make 3 worker threads that work through queue
        #   2a) worker takes ip from queue
        #   2b) worker sends 5 random-kuid find_node_req to that IP
        #   2c) worker waits for replies and saves all found ipv4 and ipv6 addresses !and ports! seperately in a list as tuples <ip, port>
        #       2c_1) timeout after 5s? 4s? (+20%!)
        #       2c_2) note down response rate?
        #   2d) worker writes all found ip-addresses to a file (thread-safety / race cond. ??)
        #   2e) worker checks if there is space in queue
        #       ---- 2e_1) if there is space, add as many ipv6 addr to queue as possible ---- (prob not possible to talk to them properly... mojito ipv6 header problem...)
        #       2e_2) add only ipv4 addresses to queue, until all contacts added or list is full
        #       2e_3) add maybe 5 ipv4 addresses to queue to get bit more variety, else we end up in one spot on dht
        #   2f) worker returns to initial state (->2a)
        # 3) keyboard interrupt

    elif _config.crawler == "testmode":
        #hexstr = "78dacafdb7a1ce62eb6dd71e55e7d445d2671a19981940e0d283c2f71e92e71dfb3866b06c3aeeb9de9091c18a0101d8189c5c1d83581818c1343794e601d2418e518e8c509a094a33036900000000ffff"
        #hexstr = "688162604005868c0c8f90b8d20c4eae8e412c0c8c609a1d4a7343691e20ed1ee2edce0ea799c0342794cf05a545a1b418941687d21240dac7d3d795154a7303f543686630cd0315e7818af340c579a1e2a2701a222f06e58b41f9e250be38940fb34f02c84707408f9b40995c40cccee011ec1ac0c810eee118c2c810181400947733720bf9ff3fc439c0939121c427589191c1d1c523848121f7df863a8badb75d7b549d5317499f696404da0234e294c486e4ade60a602339180e338539bb823c9dc4ec1eeaeac8c4141ae0ccc423c0e412eadc10c8c86816a0a6c0301be61849adfc4266a0150ecd400b9c19181831ad607407aa7bd291f16ecd2f88050cd8ad6046b2428151f24309430707d80e4606c681329d9548d399c8329dc508a8626d62cdb7386966a8eac3604319418632287131fbf83b3ba5e681cc2ee68619c4846910b32550737e5a40e98174bcce1485399340943159004d487bbd356443d75a46b0cb58b09ae7c40334cf49a5938071ac20e74d96770ee8fa2bcb0ff12856e376809df75c9b90f358b48146fcef96f07b62ca05364e01e85d5088a9892342ccc91f5f8081425ec74662f94953788021853c032352c84ff7c1631013790601000000ffff"
        #hexstr = "789c3b313f4fa7f15b61dcdc471a35a7e668ff666062000200810a08f9"
        hexstr = "6881626040058c8cac3e404a3e739dee85db8acc20210786c34c61ceaeee21deee49cceea1ae8e4c4ca101ce4c9c2a4c2ea1ce0d818c8c66016a0c39e909f56532103324773287f8043b34bb788438034d04000000ffff" #recv .. pong?
        byte_values = [int(hexstr[i:i + 2], 16) for i in range(0, len(hexstr), 2)]

        decompressor = zlib.decompressobj()
        decompressed_bytestr = b''
        hexstr_decomp = ""
        try:
            for b in byte_values:
                byte = b.to_bytes(1, "big")
                decompressed_byte = decompressor.decompress(byte)
                decompressed_bytestr += decompressed_byte
                if decompressed_byte != b'':
                    hexstr_decomp += decompressed_byte.hex()
                    print(decompressed_byte.hex())
            print(decompressed_bytestr.decode())
        except Exception as e:
            print(e)
        decompressor.flush()
        print(hexstr_decomp)
        # deflate_compress = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
        # deflate_data = deflate_compress.compress(data) + deflate_compress.flush()
        # data_decompressed = zlib.decompress(deflate_data, -zlib.MAX_WBITS)
        # print(data_decompressed)
        # print(data_decompressed.decode())
        # print(str(data_decompressed.decode()))
        exit(0)

        # text = "Test123"
        # #compress
        # deflate_compress = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)
        # deflate_data = deflate_compress.compress(text.encode()) + deflate_compress.flush()
        # print(deflate_data)
        # #decompress
        # data = zlib.decompress(deflate_data, -zlib.MAX_WBITS)
        # print(data)

    else:
        print("Unrecognized crawler type, available are <gnutella> and <mojito> (DHT)")
        exit(1)


    addrQueue = _dependants_.initAddrQueue(addrQSize=addrQSize, ip_ver=ip_ver, staticHeaderValues=staticHeaderValues)
    writeQueues = [Queue(maxsize=writeQSize), Queue(maxsize=writeQSize)]  # [HubsQ, LeavesQ]
    run_event = Event()
    run_event.set()
    workerThreads = _utilities_.get_workerThreads(target=targetFunction, run_event=run_event, num_threads=numThreads, addrQueue=addrQueue, writeQueues=writeQueues, staticHeaderValues=staticHeaderValues)
    writerThreads = _utilities_.get_writerThread(writeQueues=writeQueues, run_event=run_event)
    _utilities_.runThreads(workerThreads, writerThreads, run_event)




    # '''
    # sending_port = "00 00 00 00"  # GEHT NICHT
    # '''
    # local_kuid = str(secrets.token_hex(20))  # zufällig generierte KUID (160bit laut doku)
    #
    # # "Mojito DHT" bytes aus Wireshark rausgenommen --> aufteilen nach Position (jedes Byte hat Bedeutung) --> in Variablen und dann modifizieren. Anschließend Protokoll genau anschauen und gegen DHT testen
    # ''' message_id = "50 f4 31 02 f9 27 3e d7 33 eb 4c d6 87 d5 00 99" '''
    #
    # message_ids = []
    # for i in range(triesNum):
    #     message_ids.append(str(secrets.token_hex(16)))  # zufällig generierte msg-ID (128bit laut doku) -> x10 für 10 Outgoing Msgs
    # '''
    # message_id =  str(secrets.token_hex(16))  # zufällig generierte msg-ID (128bit laut doku) -> x10 für 10 Outgoing Msgs
    # '''
    #
    # fdht_message = "44"  # Hardcoded
    # version = "00 00"  # Major, minor... Muss evt. so bleiben?
    # '''
    # if ip_ver == 4:
    #     payload_len = f'{hex(58)[2:]} 00 00 00'  # "3a 00 00 00"  # 3a = 58  (00 00 00 evt. Padding o.ä.? big endian?) - "empirisch" bestimmt aus WS
    # else:
    #     payload_len = f'{hex(93)[2:]} 00 00 00'  # geht nicht.. WS erkennt einfach keine IPv6-Mojitopakete, und bei anderer payload_len auch keine Antworten von nodes.. Macht aber nix - 'Contact' infos sind nicht für connection sondern für mojito dht nodes - einfach z.B. 0.0.0.0 spoofen
    # '''
    # payload_len = f'{hex(58)[2:]} 00 00 00'
    # opcode = "05"  # FIND NODE REQUEST (5)
    # # Originating Contact
    # vendor = "54 45 53 54"  # "TEST", sonst z.B. "GTKG" (gtk-gnutella)
    # #vendor = "47 54 4b 47"  # GTKG
    # contact_version = "00 00"  # Major, minor
    # ''' kuid = "1b 13 c8 12 26 55 e6 18 34 d1 0c 24 0e 34 74 c2 ec b1 3b 11"  # Vorerst aus Wireshark übernommen (lsb: bf -> 11) '''
    # kuid = local_kuid
    # # Socket / Connection
    # '''
    # if ip_ver == 4:
    #     ip_version = "04"
    # elif ip_ver == 6:
    #     ip_version = "16"   # geht nicht - siehe oben (WS kann das nicht)
    # '''
    # if ip_ver == 4:
    #     ip_version = "04"
    # else:
    #     ip_version = "16"
    #
    # ip_addr = ip2Hex(public_ip, ip_ver)  # ip_addr = "2e f2 0a 34"  # '46.242.10.52'     # spoofen wie unten (s.o.), braucht der dht ja gar nicht zu wissen...
    # '''
    # ip_addr = "00 00 00 00"  # "0.0.0.0" - Wireshark kann nur 'IP Version: 4' für Mojito; alles andere wird nicht erkannt und ist nur im UDP Filter sichtbar..
    # '''
    # ''' ip_port = "c6 9a"  # '50842' ... nicht sicher warum hier nochmal... ist ja schon in Transport Layer (UDP) vermerkt... '''
    # ip_port = sending_port
    # sock_addr = ip_version + ip_addr + ip_port
    # originating_contact = vendor + contact_version + kuid + sock_addr
    #
    # instance_id = "01"  # ?
    # flags = "03"  # SHUTDOWN=1, Firewalled=1 -> 0b11 = 0x03
    # extended_len = "00 00"  # ?
    #
    # gnutella_headers = []
    # for i in range(triesNum):
    #     gnutella_headers.append(message_ids[i] + fdht_message + version + payload_len + opcode + originating_contact + instance_id + flags + extended_len)
    # '''
    # gnutella_header = message_id + fdht_message + version + payload_len + opcode + originating_contact + instance_id + flags + extended_len
    # '''
    #
    # target_kuids = []
    # for i in range(triesNum):
    #     target_kuids.append(secrets.token_hex(20))  # neue KUID zufällig generieren
    # '''
    # target_kuid = secrets.token_hex(20)  # neue 20bit KUID zufällig generieren
    # '''
    #
    #
    # ''' opcode_specific_data = "41 b3 4f 25 34 b8 d1 4d be 04 d8 fc c1 d7 f5 24 bc 7f 52 fd"  # Für diesen OPCODE (find node request) -> Target KUID (kademlia unique id) '''
    # for i in range(triesNum):
    #     mojito_msg = bytearray.fromhex(gnutella_headers[i] + target_kuids[i])
    #     sock.sendto(mojito_msg, (target_ip, target_port))
    #
    # '''
    #     for j in range(len(mojito_targets)):
    #         sock.sendto(mojito_msg, (mojito_targets[j], mojito_target_ports[j]))
    # '''
    # '''
    # findNode_packet = bytearray.fromhex(gnutella_header + target_kuid)
    # '''
    #
    # '''
    # data, replier_addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    # print(data)
    # '''
    # recvReply(sock)
    # sock.close()
