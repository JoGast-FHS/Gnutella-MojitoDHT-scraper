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
dht_ipv4_file__ipv4Mode = "../Results/MojitoDHT/v4mode__ipv4_Addresses_DHT.txt"
dht_ipv6_file__ipv4Mode = "../Results/MojitoDHT/v4mode__ipv6_Addresses_DHT.txt"
dht_ipv4_file__ipv6Mode = "../Results/MojitoDHT/v6mode__ipv4_Addresses_DHT.txt"
dht_ipv6_file__ipv6Mode = "../Results/MojitoDHT/v6mode__ipv6_Addresses_DHT.txt"

#GNUTELLA SETTINGS
gnutella_sending_ipVer = 4
# dht_num_worker_threads = 3
gnutella_socket_timeout = 7
# dht_queue_size = 100
# dht_write_queue_size = 1000
gnutella_ipv4_file = "Results/ipv4_Addresses_Gnutella.txt"
gnutella_ipv6_file = "Results/ipv6_Addresses_Gnutella.txt"
