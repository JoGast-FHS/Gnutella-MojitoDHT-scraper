



class ConnectMessage:
    @classmethod
    def handshakePacket(cls, remote_ip, listen_ip, listen_port):
        headers = {}
        banner = "GNUTELLA CONNECT/0.6"
        headers['User-Agent'] = "TEST 0.0.0.1"
        headers['Accept'] = "application/x-gnutella-packets"
        headers['X-Ultrapeer'] = "False"
        headers['X-Ultrapeer-Needed'] = "True"
        headers['Listen-IP'] = listen_ip + ":" + str(listen_port)
        headers['Remote-IP'] = remote_ip
        headers['Accept-Encoding'] = "deflate"
        #headers['GGEP'] = "0.5"
        #headers['Accept-Encoding'] = "deflate"
        return cls(ConnectMessage.fromArgs(banner, headers).toString())

    @classmethod
    def handshakePacket_crawler(cls):
        headers = {}
        banner = "GNUTELLA CONNECT/0.6"
        headers['User-Agent'] = "TEST 0.0.0.1"
        #headers['Accept'] = "application/x-gnutella-packets"
        #headers['GGEP'] = "0.5"
        headers['Crawler'] = "0.1"
        return cls(ConnectMessage.fromArgs(banner, headers).toString())

    @classmethod
    def ackPacket(cls):
        headers = {}
        banner = "GNUTELLA/0.6 200 OK"
        headers['Accept'] = "application/x-gnutella-packets"
        headers['Content-Type'] = "application/x-gnutella-packets"
        headers['Accept-Encoding'] = "deflate"
        headers['Content-Encoding'] = "deflate"
        return cls(ConnectMessage.fromArgs(banner, headers).toString())

    def toString(self):
        messagestring = self.banner + "\r\n"
        for header, val in self.headers.items():
            messagestring += f"{header}: {val}\r\n"
        #messagestring += "\r\n"
        # note: MUST be terminated with \r\n\r\n, otherwise invalid handshake packet.
        # termination string or ipv6 header before t.string will be inserted in do_handshake()
        return messagestring

    @classmethod
    def fromArgs(cls, banner, headers):
        messagestring = banner + "\r\n"
        for header, val in headers.items():
            messagestring += f"{header}: {val}\r\n"
        messagestring += "\r\n"
        return cls(messagestring)

    def __init__(self, messagestring):
        self.headers = {}
        toSplit = messagestring
        try:
            while toSplit[-2:] == "\r\n":
                toSplit = toSplit[:-2] # [:-n] to remove CRLF at end of message - !! \r and \n count as 1 char each !!
            splitMsg = toSplit.split('\r\n')
            for i, headerArg in enumerate(splitMsg):
                if i == 0:
                    self.banner = headerArg
                    if self.banner != "GNUTELLA CONNECT/0.6":
                        self.splitBanner = self.banner.partition(' ')  # .partition() instead of .split() because it keeps second ' ' between status code and -descriptor (e.g. '200 OK')
                        self.statusCode_full = self.splitBanner[2]  # self.banner[1] is separator itself, so ' ' here
                        self.statusCode = int(self.statusCode_full.split(' ')[0], 10)
                    continue
                elif i == 1 and headerArg == '':    # some servents seem to send empty line between header and body
                    continue

                try:
                    headerTuple = headerArg.split(': ')
                    headerName = headerTuple[0]
                    headerVal = headerTuple[1].replace('\r\n', '')  # remove CRLF at beginning of header value, if present (sometimes the case with 'Peers' header, for example)
                    self.headers[headerName] = headerVal
                except Exception:
                    continue
        except Exception as e:
            print("Error while creating ConnectMessage: " + str(e))