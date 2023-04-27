


class HandshakePacket:
    def to_str(self):
        return self.handshake_str

    def __init__(self, local_ip, local_port, target_ip):
        self.handshake_str = \
            "GNUTELLA CONNECT / 0.6\n"\
            "User - Agent: TEST 0.0.0.1\n"\
            "Accept: application / x - gnutella2\n"\
            "X - Ultrapeer: False\n" \
            "X - Ultrapeer - Needed: True\n" \
            f"Listen - IP: {local_ip}:{local_port}\n" \
            f"Remote - IP: {target_ip}\n" \
            "Accept - Encoding: deflate\n" \

    def __str__(self):
        return self.handshake_str
