import Gnutella_HandshakePacket
import _utilities_

def do_handshake(sock, target_ip):
    local_ip = _utilities_.get_public_ip(4)
    local_port = sock.getsockname()[1]
    message = Gnutella_HandshakePacket.HandshakePacket(local_ip, local_port, target_ip)
    sock.connect((target_ip, 6346))
    sock.send(message.to_str().encode())
    response = sock.recv(1024).decode()
    print(response)



def ping(sock, target_ip):
    do_handshake(sock, target_ip)



