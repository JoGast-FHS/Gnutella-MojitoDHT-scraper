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
        self.payloadlen = str(len(payload)).zfill(2*4)  # payload length is 4 bytes long
        self.payload = payload

        self.message_str = self.message_id + self.payloadtype + self.ttl + self.hops + self.payloadlen + self.payload
        #self.message_hex = hex(int(self.message_id, 16))[2:]



# recv:
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00     01  01  05    4c000000     1f69  ae2dd0db  21030000  00004000 c30256434547544b4762034755454102025550430209240244554380510101365026006c67607f761c00000000000019b903544c53408344485443000001
# msg id                                            pong ttl  hops  payl.len     port   ipAddr   nr.Files  nr. kb    GGEP-Block