import DHT_GnutellaHeader
import DHT_GnutellaPayload


class GnutellaMessage:
    @classmethod
    def fromArgs(cls, args):
        for arg, val in args.items():
            #TODO
            break

    def __init__(self, messagebytes):
        self.header = DHT_GnutellaHeader.GnutellaHeader(messagebytes)
        self.header_len = self.header.headerLength
        self.payload_len = len(messagebytes) - self.header_len
        self.payloadtype = self.header.get_arg('opcode')  # normalerweise 5 (find node req.) oder 6 (find node resp.)
        self.payload = DHT_GnutellaPayload.GnutellaPayload(messagebytes[(self.header_len * 2):], self.payloadtype)  # *2: Bytes->Digits
        if self.payload.messagetype == "Reply":
            self.ipv6_addresses_found = self.payload.ipv6_addresses
            self.ipv4_addresses_found = self.payload.ipv4_addresses
            self.ipv6_ports_found = self.payload.ipv6_ports
            self.ipv4_ports_found = self.payload.ipv4_ports

    def __str__(self):
        return "HEADER:\n\n" \
               f"{self.header}\n" \
               "\n\n\n" \
               "Payload:\n\n" \
               f"{self.payload}\n"
