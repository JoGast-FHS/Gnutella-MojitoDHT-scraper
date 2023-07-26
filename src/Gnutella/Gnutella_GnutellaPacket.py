import secrets
from src._general_._utilities_ import replaceStr


class GnutellaPacket:
    def toHex(self):
        return self.message_hex

    def toString(self):
        return self.message_str

    @classmethod
    def crawlerPingv4(cls):
        return cls("00", "02", "00", "")

    def __init__(self, payloadtype, ttl, hops, payload):
        msgID = secrets.token_hex(16)
        replaceStr(str=msgID, index=15, newStr="ff") # see Gnutella 0.6 documentation - shows that this is a 'modern' Servent
        replaceStr(str=msgID, index=30, newStr="00") # see Gnutella 0.6 documentation - reserved for future use
        # msgID[15] = 0xf  # see Gnutella 0.6 documentation - shows that this is a 'modern' Servent
        # msgID[16] = 0xf
        # msgID[30] = 0x0  # see Gnutella 0.6 documentation - reserved for future use
        # msgID[31] = 0x0
        self.message_id = msgID
        self.payloadtype = payloadtype.zfill(2)
        self.ttl = ttl.zfill(2)
        self.hops = hops.zfill(2)
        self.payloadlen = str(len(payload)).zfill(6)
        self.payload = payload

        self.message_str = self.message_id + self.payloadtype + self.ttl + self.hops + self.payloadlen + self.payload
        #self.message_hex = hex(int(self.message_id, 16))[2:]


