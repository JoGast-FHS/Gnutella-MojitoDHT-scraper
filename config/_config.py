# Crawlen von "gnutella" oder "mojito" (DHT)
crawler = "gnutella"

#MOJITO DHT SETTINGS
dht_ip_version = 4  # Was in den Gnutella-Header geschrieben wird (bei v4 aber tatsächlichem v6 dann auch (falsche) public IP) - Offenbar nicht für IPv6 vorgesehen?
dht_sending_ipVer = 4  # Von welcher IP (v4/v6) tatsächlich gesendet wird
dht_number_of_requests_per_address = 5
dht_num_worker_threads = 3
dht_socket_timeout = 3
dht_queue_size = 100
dht_write_queue_size = 1000
dht_ipv4_file__ipv4Mode = "Results/MojitoDHT/v4mode/IPv4_Addr/Addr_found.txt"
dht_ipv6_file__ipv4Mode = "Results/MojitoDHT/v4mode/IPv6_Addr/Addr_found.txt"
dht_ipv4_file__ipv6Mode = "Results/MojitoDHT/v6mode/IPv4_Addr/Addr_found.txt"
dht_ipv6_file__ipv6Mode = "Results/MojitoDHT/v6mode/IPv6_Addr/Addr_found.txt"

#GNUTELLA SETTINGS
gnutella_sending_ipVer = 4
gnutella_crawlerHeader = True    # Anstatt normalem Ping wird ein Crawl-Ping gesendet. Siehe Gnutella_HandshakePacket-Crawler.py
gnutella_ip6Header = False       # GGEP extension header für IPv6-Adressen wird zu den Handshake-Paketen hinzugefügt
# dht_num_worker_threads = 3
gnutella_socket_timeout = 7
# dht_queue_size = 100
# dht_write_queue_size = 1000
gnutella_ipv4_file = "Results/Gnutella/IPv4_Addr/Addr_found.txt"
gnutella_ipv6_file = "Results/Gnutella/IPv6_Addr/Addr_found.txt"
