import secrets
from config import _config
from src._general_._utilities_ import replaceStr, hex2ip, swap_byteorder


class GnutellaPacket:
    def toHex(self):
        return self.message_hex

    def toString(self):
        return self.message_str

    def processPayload(self):
        bytelen = 2  # easier handling of string using bytes instead of string indices
        payloadlen_bytes = int(self.payloadlen, 16) * bytelen
        if self.payloadlen == 0:
            print("Payload Processing: No payload found.")
            return
        payload = self.payload
        port = int(swap_byteorder(payload[:2*bytelen]), 16)  # all little endian (see G0.6 doc) --> big endian
        ip_addr = hex2ip(payload[2*bytelen:6*bytelen], 4)  # ONLY IPv4 capable, to best of knowledge; ip bytes NOT to be swapped
        files_nr = int(swap_byteorder(payload[6*bytelen:10*bytelen]), 16)
        kb_nr = int(swap_byteorder(payload[10*bytelen:14*bytelen]), 16)
        ggep_block = swap_byteorder(payload[14*bytelen:payloadlen_bytes])
        remainder = payload[payloadlen_bytes:]  # Payload Length signifies end of payload for ONE Header + Payload. After that, more may have been transmitted.
        #print(f"Pong Payload Processing:\nPort: {port}\nIP-Addr.: {ip_addr}\nNr. Files: {files_nr}\nNr. kB: {kb_nr}\nGGEP Block: {ggep_block}\nRemainder: {remainder}")  # verbose
        print(f"Pong returned ({ip_addr}, {port})")
        return remainder, (ip_addr, port)

    @classmethod
    def fromString(cls, pongStr):
        pong_arr = [pongStr[i:i + 2] for i in range(0, len(pongStr), 2)]
        msg_id = swap_byteorder(''.join(pong_arr[:16]))  # little Endian->big Endian
        payload_type = ''.join(pong_arr[16:17])  # don't have to swap single-byte values
        ttl = ''.join(pong_arr[17:18])
        hops = ''.join(pong_arr[18:19])
        payload_len = swap_byteorder(''.join(pong_arr[19:23]))
        payload = ''.join(pong_arr[23:])  # DON'T swap byteorder, else will be done 2x when fed into payload processing again later (and headerbytes will be swapped to back)
        return cls(payload_type, ttl, hops, payload, msg_id, payload_len)

    @classmethod
    def crawlerPingv4(cls):
        return cls("00", "02", "00", "")


    def __init__(self, payloadtype, ttl, hops, payload, msgID="", payloadlen=""):
        if msgID == "":
            msgID = secrets.token_hex(16)
            replaceStr(str=msgID, index=15, newStr="ff") # see Gnutella 0.6 documentation - shows that this is a 'modern' Servent
            replaceStr(str=msgID, index=30, newStr="00") # see Gnutella 0.6 documentation - reserved for future use
        self.message_id = msgID
        self.payloadtype = payloadtype.zfill(2)
        self.ttl = ttl.zfill(2)
        self.hops = hops.zfill(2)
        if payloadlen == "":
            self.payloadlen = swap_byteorder(hex(len(payload))[2:].zfill(2*4))  # payload length takes 4 bytes
        else:
            self.payloadlen = hex(int(payloadlen, 16))[2:].zfill(2*4)
        self.payload = payload

        self.message_str = self.message_id + self.payloadtype + self.ttl + self.hops + self.payloadlen + self.payload
        #self.message_hex = hex(int(self.message_id, 16))[2:]



# recv:
# 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00     01  01  05    4c000000     1f69  ae2dd0db  21030000  00004000 c30256434547544b4762034755454102025550430209240244554380510101365026006c67607f761c00000000000019b903544c53408344485443000001
# msg id                                            pong ttl  hops  payl.len     port   ipAddr   nr.Files  nr. kb    GGEP-Block