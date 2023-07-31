# Hardcoded IP-Addr./Port - Tuples to bootstrap and fall back on
#-----------------------------------------------------------------------------------
# Values gathered empirically and might not work anymore in the future!
# In that case, substitute with addr/port tuples taken from e.g. widely
# used servents' traffic, since they implement more sophisticated bootstrapping.

# Mojito DHT
dht_targets_ipv4 = [("188.136.234.186", 44858),
                    ("74.194.163.160", 37041),
                    ("194.163.180.126", 10825)]

dht_targets_ipv6 = [("2a02:2168:b01:5d2d::2", 50842),
                    ("2a01:6ee0:1::ffff:bae", 53489),
                    ("2a00:23c4:f4d8:1e00:3504:c92e:3fc6:fee5", 9915),
                    ("2001:19f0:7400:8808::1:1", 15793),
                    ("2a02:c206:2066:1372::1", 10825),
                    ("2401:c080:1800:48e1::1:1", 50733),
                    ("2001:d08:d4:b220:1539:3492:7558:ba51", 39524),
                    ("2601:646:9880:6c00:71b3:f53:9853:fe75", 32173),
                    ("2001:d08:d4:b220:48d8:3b8f:1e46:35fb", 39524)]


# Gnutella
gnutella_targets_ipv4 = [("202.27.193.6", 6346),  #gnutella2
                         ("88.164.223.61", 6346),
                         ("172.111.233.123", 51500),
                         ("104.28.243.200", 6346),
                         ("65.31.202.72", 6346),
                         ("67.170.110.210", 6346),

                         ("86.157.248.213", 6346),  #gnutella1
                         ("52.212.171.135", 6346),
                         ("82.15.220.175", 6346)]


gnutella_targets_ipv6 = [("2a02:2168:b01:5d2d::2", 50842),
                         ("2a01:6ee0:1::ffff:bae", 53489),
                         ("2a00:23c4:f4d8:1e00:3504:c92e:3fc6:fee5", 9915),
                         ("2001:19f0:7400:8808::1:1", 15793),
                         ("2a02:c206:2066:1372::1", 10825),
                         ("2401:c080:1800:48e1::1:1", 50733),
                         ("2001:d08:d4:b220:1539:3492:7558:ba51", 39524)]
