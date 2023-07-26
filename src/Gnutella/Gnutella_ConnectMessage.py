



class ConnectMessage:
    @classmethod
    def handshakePacket(cls, target_ip):
        headers = {}
        banner = "GNUTELLA CONNECT/0.6"
        headers['User-Agent'] = "TEST 0.0.0.1"
        headers['Accept'] = "application/x-gnutella2"
        headers['X-Ultrapeer'] = "False"
        headers['X-Ultrapeer-Needed'] = "True"
        headers['Remote-IP'] = target_ip
        #headers['Accept-Encoding'] = "deflate"
        return cls(ConnectMessage.fromArgs(banner, headers).toString())

    @classmethod
    def ackPacket(cls):
        headers = {}
        banner = "GNUTELLA/0.6 200 OK"
        headers['Accept'] = "application/x-gnutella2"
        headers['Content-Type'] = "application/x-gnutella2"
        return cls(ConnectMessage.fromArgs(banner, headers).toString())

    def toString(self):
        messagestring = self.banner + "\r\n"
        for header, val in self.headers.items():
            messagestring += f"{header}: {val}\r\n"
        messagestring += "\r\n"
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
        splitMsg = messagestring[:-4].split('\r\n')  # [:-4] to remove CRLF at end of message
        for i, headerArg in enumerate(splitMsg):
            if i == 0:
                self.banner = headerArg
                if self.banner != "GNUTELLA CONNECT/0.6":
                    self.splitBanner = self.banner.partition(' ')  # .partition() instead of .split() because it keeps second ' ' between status code and -descriptor (e.g. '200 OK')
                    self.statusCode_full = self.splitBanner[2]  # self.banner[1] is separator itself, so ' ' here
                    self.statusCode = int(self.statusCode_full.split(' ')[0], 10)
                continue
            headerTuple = headerArg.split(': ')
            headerName = headerTuple[0]
            headerVal = headerTuple[1]
            self.headers[headerName] = headerVal