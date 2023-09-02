# Gnutella-MojitoDHT-scraper
Program to scrape IP-Addresses from both Gnutella Network and Mojito DHT.
Made specifically to examine IPv6 capabilities.

Created during and for the Master Thesis "IPv6 in the Gnutella P2P network and the Mojito DHT".
By Jonas Gasteiger. 



Some documentation is provided through comments within the code.
In general, the program may be used to crawl either Mojito or Gnutella.

# Crawling the Mojito DHT
If Mojito is to be crawled, the variables in _config.py are to be adjusted in the following:

- crawler = “mojito”
- dht ip version = 4
- dht sending ipVer = 4

Furthermore, in the _targets.py file, some reachable DHT nodes need to be entered. These can be obtained by e.g. running a servent like GTK-Gnutella and capturing Mojito traffic.


# Crawling Gnutella
Two approaches exist for crawling Gnutella. The first one, called the 'Handshake' approach, utilizes a "Crawler" header in the Gnutella handshake and may thus crawl both G1 and G2 nodes.
The variables in _config.py need to be adjusted in the following:

- crawler = “gnutella”
- gnutella crawlerHeader = “True”
- gnutella ip6Header = “False”
- gnutella sending ipVer = 4

The 'Ping' approach, on the other hand, utilizes G1 binary messages (Crawler Ping) in order to request known peers and leaves from other nodes. Can only crawl Gnutella(1).

- crawler = “gnutella”
- gnutella crawlerHeader = “False”
- gnutella sending ipVer = 4

For both approaches, the _targets.py file needs to be updated with some reachable nodes. These can be obtained by looking at the connections a servent like GTK-Gnutella establishes, or by directly consulting a GWebCache like "Bazooka!".


For further information, the Master Thesis itself may prove useful.
