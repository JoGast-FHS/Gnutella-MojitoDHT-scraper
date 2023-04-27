crawler = "gnutella"  # Crawlen von "gnutella" oder "mojito" (DHT)

#MOJITO DHT SETTINGS
dht_ip_version = 4  # Was in den Gnutella-Header geschrieben wird (bei v4 aber tatsächlichem v6 dann auch (falsche) public IP) - Offenbar nicht für IPv6 vorgesehen?
dht_sending_ipVer = 6  # Von welcher IP (v4/v6) tatsächlich gesendet wird
dht_number_of_requests_per_address = 5
dht_num_worker_threads = 3
dht_socket_timeout = 3
dht_queue_size = 100
dht_write_queue_size = 1000
dht_ipv4_file = "Results/ipv4_Addresses_DHT.txt"
dht_ipv6_file = "Results/ipv6_Addresses_DHT.txt"

dht_target_addresses_ipv4 = ["188.136.234.186", "74.194.163.160", "194.163.180.126"]
dht_target_ports_ipv4 = [44858, 37041, 10825]
dht_target_addresses_ipv6 = ["2a02:2168:b01:5d2d::2", "2a01:6ee0:1::ffff:bae", "2a00:23c4:f4d8:1e00:3504:c92e:3fc6:fee5", "2001:19f0:7400:8808::1:1", "2a02:c206:2066:1372::1", "2401:c080:1800:48e1::1:1"]  # nr.1 kennt offenbar viel mehr ipv6 peers...
dht_target_ports_ipv6 = [50842, 53489, 9915, 15793, 10825, 50733]



#GNUTELLA SETTINGS
gnutella_ipv4_file = "Results/ipv4_Addresses_Gnutella.txt"
gnutella_ipv6_file = "Results/ipv6_Addresses_Gnutella.txt"

gnutella_target_addresses_ipv4 = ["188.136.234.186", "74.194.163.160", "194.163.180.126"]
gnutella_target_ports_ipv4 = [44858, 37041, 10825]
gnutella_target_addresses_ipv6 = ["2a02:2168:b01:5d2d::2", "2a01:6ee0:1::ffff:bae", "2a00:23c4:f4d8:1e00:3504:c92e:3fc6:fee5", "2001:19f0:7400:8808::1:1", "2a02:c206:2066:1372::1", "2401:c080:1800:48e1::1:1"]  # nr.1 kennt offenbar viel mehr ipv6 peers...
gnutella_target_ports_ipv6 = [50842, 53489, 9915, 15793, 10825, 50733]
