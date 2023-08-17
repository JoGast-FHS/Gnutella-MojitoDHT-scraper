# Crawl "gnutella" or "mojito" (DHT)
crawler = "gnutella"

#MOJITO DHT SETTINGS
dht_ip_version = 4  # Was in den Gnutella-Header geschrieben wird (bei v4 aber tatsächlichem v6 dann auch (falsche) public IP) - Offenbar nicht für IPv6 vorgesehen?
dht_sending_ipVer = 4  # actual IP version used for sending packets
dht_num_requests = 2
dht_num_worker_threads = 3
dht_socket_timeout = 3
dht_write_queue_size = 1000
dht_addr_queue_size = 1000
dht_ipv4_file__ipv4Mode = "Results/MojitoDHT/v4mode/IPv4_Addr/Addr_found.txt"
dht_ipv6_file__ipv4Mode = "Results/MojitoDHT/v4mode/IPv6_Addr/Addr_found.txt"
dht_ipv4_file__ipv6Mode = "Results/MojitoDHT/v6mode/IPv4_Addr/Addr_found.txt"
dht_ipv6_file__ipv6Mode = "Results/MojitoDHT/v6mode/IPv6_Addr/Addr_found.txt"

#GNUTELLA SETTINGS
gnutella_sending_ipVer = 4
gnutella_crawlerHeader = False    # Anstatt normalem Ping wird ein Crawl-Ping gesendet. Siehe Gnutella_HandshakePacket-Crawler.py
gnutella_ip6Header = False       # GGEP extension header for IPv6-Adressen will be added to handshake packets - NOT SUPPORTED BY ALL SERVENTS
gnutella_ip6HeaderString = "x-Features: IP/6.4\r\n"
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