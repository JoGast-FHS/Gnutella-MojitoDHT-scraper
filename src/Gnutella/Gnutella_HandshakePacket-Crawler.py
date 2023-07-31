#Crawler Handshake-Paket nach https://web.archive.org/web/20080624014943/http://wiki.limewire.org/index.php?title=Communicating_Network_Topology_Information


class HandshakePacket:
    def to_str(self):
        return self.handshake_str

    def __init__(self, local_ip, local_port, target_ip):
        self.handshake_str = \
            "GNUTELLA CONNECT/0.6\r\n" \
            "User-Agent: TEST 0.0.0.1 \r\n" \
            "X-Ultrapeer: False\r\n" \
            "Query-Routing: 0.1\r\n" \
            "Crawler: 0.1\r\n"
        # note: MUSS MIT \r\n\r\n terminiert werden, sonst ungültiges Handshake-Paket
        # termination string oder ipv6 header vor t.string wird in do_handshake() eingefügt

    def __str__(self):
        return self.handshake_str
