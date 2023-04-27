




def get_header_argLens(ip_ver):
    # Gnutella Header values - bytelenghts
    headerArgumentlengths = {
        'msgId_len':        16,  # BYTES !! (digits = bytes*2)
        'fdhtMsg_len':      1,   #
        'verMajor_len':     1,   #
        'verMinor_len':     1,   #
        'payloadLen_len':   4,   #
        'opcode_len':       1,   #
        'vendor_len':       4,   #
        'cVerMajor_len':    1,   #
        'cVerMinor_len':    1,   #
        'kuid_len':         20,  #
        'ipVer_len':        1,   #
        'ipAddr_len':       4,   # 4 for ipv4, 16 for v6
        'ipPort_len':       2,   #
        'instanceId_len':   1,   #
        'flags_len':        1,   #
        'extLength_len':    2,   #
    }
    if ip_ver == 4:
        headerArgumentlengths['ipAddr_len'] = 4
    else:
        headerArgumentlengths['ipAddr_len'] = 16
    return headerArgumentlengths


def get_total_headerLen(ip_ver):
    headerArgumentlengths = get_header_argLens(ip_ver)
    headerLength = 0
    for argument, argumentLen in headerArgumentlengths.items():
        headerLength += argumentLen
    return headerLength


def get_nth_key(dictionary, n=0):
    if n < 0:
        n += len(dictionary)
    for i, (key, val) in enumerate(dictionary.items()):
        if i == n:
            return key
    raise IndexError("dictionary index out of range")


class GnutellaHeader:
    def __get_headerbytes(self, messagebytes, ip_ver):  # gibt die Bytes von der Message zurück, die den Gnutellaheader ausmachen. Anders für IPv4 und IPv6 und muss im Programm-Flow zweimal ausgeführt werden
        self.headerArgumentlengths = get_header_argLens(ip_ver)
        self.headerLength = get_total_headerLen(ip_ver)
        headerbytes = messagebytes[:(self.headerLength * 2)]
        return headerbytes  # bytes -> hex-digits

    def get_arg(self, arg):
        return self.headerArguments[arg]

    def to_hexstr(self):
        return self.headerbytes

    @classmethod
    def fromArgs(cls, headerArguments):  # statt mit bytestring mit Parametern instantiieren
        messagebytes = ""
        for argument, value in headerArguments.items():
            argumentbytes = value
            messagebytes += argumentbytes
        return cls(messagebytes)

    def __init__(self, messagebytes):
        self.headerArguments = {
            'msgId':        "",
            'fdhtMsg':      "",
            'verMajor':     "",
            'verMinor':     "",
            'payloadLen':   "",
            'opcode':       "",
            'vendor':       "",
            'cVerMajor':    "",
            'cVerMinor':    "",
            'kuid':         "",
            'ipVer':        "",
            'ipAddr':       "",
            'ipPort':       "",
            'instanceId':   "",
            'flags':        "",
            'extLength':    "",
        }
        self.headerbytes = self.__get_headerbytes(messagebytes=messagebytes, ip_ver=4)
        v6flag = False
        curr_digit = 0
        for i in range(len(self.headerArguments)):
            curr_key = get_nth_key(self.headerArguments, i)
            if curr_key == 'ipAddr' and v6flag:
                argDigits = 16 * 2  # ipv6 Adresslänge
            else:
                argDigits = self.headerArgumentlengths[get_nth_key(self.headerArgumentlengths, i)] * 2  # can't address dict entries via index, only key. So this is a workaround.
            self.headerArguments[curr_key] = self.headerbytes[curr_digit:(curr_digit + argDigits)]
            curr_digit = curr_digit + argDigits
            if curr_key == 'ipVer' and self.headerArguments['ipVer'] == "10":  # !! 0x10 = 0d16 !!  IPv4 oder IPv6 - Anpassung d. Adresslängen (Flag setzen, weil Länge des nächsten Headerarguments geändert werden muss, nicht das derzeitige)
                v6flag = True
                self.headerbytes = self.__get_headerbytes(messagebytes=messagebytes, ip_ver=6)
        return

    def __str__(self):
        print()
        return f"MessageID: 0x{self.headerArguments['msgId']}\n" \
               f"FDHT-Msg: 0x{self.headerArguments['fdhtMsg']}\n" \
               f"Version Major: {int(self.headerArguments['verMajor'], 16)}\n" \
               f"Version Minor: {int(self.headerArguments['verMinor'], 16)}\n" \
               f"Payload Length: {int(self.headerArguments['payloadLen'], 16)}\n" \
               f"OPCODE: {int(self.headerArguments['opcode'], 16)}\n" \
               f"Vendor: {bytearray.fromhex(self.headerArguments['vendor']).decode()}\n" \
               f"Contact Version Major: {int(self.headerArguments['cVerMajor'], 16)}\n" \
               f"Contact Version Minor: {int(self.headerArguments['cVerMinor'], 16)}\n" \
               f"KUID: 0x{self.headerArguments['kuid']}\n" \
               f"IP Version: {int(self.headerArguments['ipVer'], 16)}\n" \
               f"IP Address: {int(self.headerArguments['ipAddr'], 16)}\n" \
               f"Port: {int(self.headerArguments['ipPort'], 16)}\n" \
               f"Instance ID: {int(self.headerArguments['instanceId'], 16)}\n" \
               f"Flags: 0x{self.headerArguments['flags']}\n" \
               f"Extended Length: {int(self.headerArguments['extLength'], 16)}\n"
