from threading import Event
from queue import Queue
import DHT_utilities
import config
import socket
import Gnutella_utilities
import _utilities_


if __name__ == "__main__":
    if config.crawler == "gnutella":
        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        sock.bind((_utilities_.get_local_ip(4), 12345))
        Gnutella_utilities.ping(sock, "78.192.163.71")

    elif config.crawler == "mojito":
        staticHeaderValues = DHT_utilities.get_headerConstants()
        addressQueue = DHT_utilities.initAddrQueue(staticHeaderValues=staticHeaderValues, ip_ver=config.dht_sending_ipVer)
        writeQueue = Queue(maxsize=config.dht_write_queue_size)
        run_event = Event()
        run_event.set()

        workerThreads = DHT_utilities.get_workerThreads(staticHeaderValues=staticHeaderValues, run_event=run_event, num_threads=config.dht_num_worker_threads, addrQueue=addressQueue, writeQueue=writeQueue)
        writerThread = DHT_utilities.get_writerThread(writeQueue=writeQueue, run_event=run_event)
        DHT_utilities.runThreads(workerThreads, writerThread, run_event)

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
        #       2e_3) add maybe 5 ipv4 addressses to queue to get bit more variety, else we end up in one spot on dht
        #   2f) worker returns to initial state (->2a)
        # 3) keyboard interrupt

    else:
        print("Unrecognized crawler type")

















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
