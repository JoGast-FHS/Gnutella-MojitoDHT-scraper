from src._general_ import _utilities_


class GnutellaPayload:

    def get_messagetype(self, opcode):
        if opcode == "05":  # find node request
            return "Request"
        elif opcode == "06":  # find node reply
            return "Reply"
        else:
            return "Unknown"


    def __init__(self, payloadbytes, opcode):
        self.messagetype = self.get_messagetype(opcode)
        self.payloadbytes = payloadbytes
        self.payload = {'payload_raw': payloadbytes}  # vmtl. später auskommentieren, um Ressourcen zu schonen

        if opcode == "05":  # find node request
            self.payload['kuid'] = payloadbytes

        elif opcode == "06":  # find node reply
            self.contacts = []
            self.ipv4_addresses = []
            self.ipv4_ports = []
            self.ipv6_addresses = []
            self.ipv6_ports = []

            secTokenLength = payloadbytes[0:2]  # diese Längen sind konstant bei opcode 6. Da nur drei Metainformationen hier einfach gehardcoded.
            secToken = payloadbytes[2:10]
            contactCount = payloadbytes[10:12]
            self.payload['security_token_length'] = secTokenLength
            self.payload['security_token'] = secToken
            self.payload['contact_count'] = int(contactCount, 16)

            curr_digit = 12  # Parserstand nach Metainformationen
            for i in range(self.payload['contact_count']):
                contactArguments = {
                    'vendor':       0x04,
                    'cVerMajor':    0x01,  # kleiner Hack zum Sparen von Ressourcen und Aufwand - Felder sind mit ihren Längen im messagestream initialisiert.
                    'cVerMinor':    0x01,  # Alles in Byte, nicht Digits
                    'kuid':         0x14,  # 0d20 -> 0x14
                    'ipVer':        0x01,
                    'ipAddr':       0x04,  # 04 oder 16
                    'ipPort':       0x02,
                }
                v6flag = False
                for arg, val in contactArguments.items():
                    if arg == 'ipVer' and payloadbytes[curr_digit:(curr_digit + contactArguments['ipVer']*2)] != "04":  # !! 0d16 -> 0x10 !!   IPv4 oder IPv6 - Anpassung d. Adresslängen (Flag setzen, weil Länge des nächsten Arguments geändert werden muss, nicht das derzeitige)
                        v6flag = True
                    if arg == 'ipAddr' and v6flag:
                        val = 0x10  # 0d16 (Bytes Länge d. Adresse) -> 0x10
                    next_digit = curr_digit + int(val)*2  # Hack von oben (*2 wg. Byte->Digits)
                    contactArguments[arg] = payloadbytes[curr_digit:next_digit]  # Überschreiben.. Länge->Value
                    curr_digit = next_digit
                    if arg == 'ipAddr':
                        if v6flag:
                            self.ipv6_addresses.append(_utilities_.hex2ip(contactArguments['ipAddr'], 6))
                            print(f"Added ipv6-addr to arr")
                        else:
                            self.ipv4_addresses.append(_utilities_.hex2ip(contactArguments['ipAddr'], 4))
                    elif arg == 'ipPort':
                        if v6flag:
                            self.ipv6_ports.append(int(contactArguments['ipPort'], 16))
                            v6flag = False
                        else:
                            self.ipv4_ports.append(int(contactArguments['ipPort'], 16))

                self.contacts.append(contactArguments)
                self.payload[f'contact{i}'] = contactArguments
        else:  # unknown
            print("Unknown message type (opcode) encountered, not processing payload!")

        return


    def __str__(self):
        if self.messagetype == "Request":
            return f"KUID: {self.payloadbytes['kuid']}"

        elif self.messagetype == "Reply":
            metaInf_str = f"Security Token Length: {self.payload['security_token_length']}\n" \
                          f"Security Token: {self.payload['security_token']}\n" \
                          f"Contact Count: {self.payload['contact_count']}\n\n"
            contacts_str = ""

            for i in range(self.payload['contact_count']):
                contact = self.contacts[i]
                contact_str = f"Contact #{i}:\n" \
                              f"Vendor: {bytearray.fromhex(contact['vendor'])}\n" \
                              f"Version Major: {contact['cVerMajor']}\n" \
                              f"Version Minor: {contact['cVerMinor']}\n" \
                              f"KUID: {contact['kuid']}\n" \
                              f"IP Version: {contact['ipVer']}\n" \
                              f"IP Address: {contact['ipAddr']}\n" \
                              f"IP Port: {contact['ipPort']}\n\n"
                contacts_str = contacts_str + contact_str

            return metaInf_str + contacts_str

        else:
            return "UNKNOWN MESSAGETYPE - cannot process payload\n" \




