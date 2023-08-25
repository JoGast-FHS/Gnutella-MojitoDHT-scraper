# Crawl "gnutella" or "mojito" (DHT)
crawler = "mojito"

#MOJITO DHT SETTINGS
dht_ip_version = 4  # What is written into the requests 'Gnutella Header' -> NEEDS TO BE SET TO 4, even if IPv6 is used for connection !
dht_sending_ipVer = 6  # actual IP version used for sending packets
dht_num_requests = 3  # number of requests sent to one node. Nodes may know more than returnable  max. of 20 other nodes
dht_num_worker_threads = 1
dht_socket_timeout = 5
dht_write_queue_size = 1000
dht_addr_queue_size = 1000
dht_ipv4_file__ipv4Mode = "Results/MojitoDHT/v4mode/Nodesv4.txt"
dht_ipv6_file__ipv4Mode = "Results/MojitoDHT/v4mode/Nodesv6.txt"
dht_ipv4_file__ipv6Mode = "Results/MojitoDHT/v6mode/Nodesv4.txt"
dht_ipv6_file__ipv6Mode = "Results/MojitoDHT/v6mode/Nodesv6.txt"

#GNUTELLA SETTINGS
gnutella_sending_ipVer = 4  # ! Leave at 4 for now, IPv6 logic mostly implemented but no IPv6 seed nodes !
gnutella_crawlerHeader = True  # If 'True': Using Header "Crawler". If 'False': Using Gnutella1 Crawler-Ping.
gnutella_ip6Header = False  # GGEP extension header for IPv6 addresses will be added to handshake packets - NOT SUPPORTED BY ALL SERVENTS
gnutella_ip6HeaderString = "GGEP: 0.5\r\nx-Features: IP/6.0\r\n"
gnutella_num_requests = 1
gnutella_num_worker_threads = 1
gnutella_socket_timeout = 6
gnutella_write_queue_size = 1000
gnutella_addr_queue_size = 1000
gnutella_ipv4_file_leaves_Ping = "Results/Gnutella/IPv4_Addr/Ping/Leaves4.txt"
gnutella_ipv4_file_hubs_Ping = "Results/Gnutella/IPv4_Addr/Ping/Hubs4.txt"
gnutella_ipv6_file_leaves_Ping = "Results/Gnutella/IPv6_Addr/Ping/Leaves6.txt"
gnutella_ipv6_file_hubs_Ping = "Results/Gnutella/IPv6_Addr/Ping/Hubs6.txt"
gnutella_ipv4_file_leaves_Crawler = "Results/Gnutella/IPv4_Addr/Crawler/Leaves4.txt"
gnutella_ipv4_file_hubs_Crawler = "Results/Gnutella/IPv4_Addr/Crawler/Hubs4.txt"
gnutella_ipv6_file_leaves_Crawler = "Results/Gnutella/IPv6_Addr/Crawler/Leaves6.txt"
gnutella_ipv6_file_hubs_Crawler = "Results/Gnutella/IPv6_Addr/Crawler/Hubs6.txt"