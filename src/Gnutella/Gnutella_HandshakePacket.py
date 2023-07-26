


class HandshakePacket:
    def to_str(self):
        return self.handshake_str

    def __init__(self, local_ip, local_port, target_ip):
        self.handshake_str = \
            "GNUTELLA CONNECT/0.6\r\n" \
            "User-Agent: TEST 0.0.0.1 \r\n" \
            "Accept: application/x-gnutella2\r\n" \
            "X-Ultrapeer: False\r\n" \
            "X-Ultrapeer-Needed: True\r\n" \
            f"Remote-IP: {target_ip}\r\n" \
            "Accept-Encoding: deflate\r\n" \
            "\r\n"

    def __str__(self):
        return self.handshake_str
