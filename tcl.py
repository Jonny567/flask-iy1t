import socket
import threading
import select
import struct
import re
from urllib.request import urlopen
import time

class TCLTVRemote:
    def __init__(self):
        self.ip = None
        self.port = 4123
        self.client_socket = None

    def find_tcl_tv(self):
        clnt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clnt.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        srvr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        mreq = struct.pack("4sl", socket.inet_aton('239.255.255.250'), socket.INADDR_ANY)
        srvr.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        srvr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srvr.bind(('', 1900))

        for _ in range(1, 10):
            msearch = ("M-SEARCH * HTTP/1.1\r\nHOST:239.255.255.250:1900\r\n"
                       "ST:upnp:rootdevice\r\nMAN:ssdp:discover\r\nMX:2\r\n\r\n")
            clnt.sendto(msearch.encode('utf-8'), ('239.255.255.250', 1900))

            srvr.setblocking(0)
            while select.select([srvr], [], [], 1.0)[0]:
                response = srvr.recv(1024).decode('utf-8')
                location = re.search(r'LOCATION: ([^\r]*)', response)
                if location is None:
                    continue
                desc_url = location.group(1)
                address = re.search(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', desc_url)
                if address is None:
                    continue
                self.ip = address.group(0)

                rsp = urlopen(desc_url).read().decode('utf-8')
                friendly_name = re.search(
                    r'<friendlyName>([^<]*)</friendlyName>',
                    rsp
                )
                manufacturer = re.search(
                    r'<manufacturer>([^<]*)</manufacturer>',
                    rsp
                )

                if manufacturer is not None and friendly_name is not None and manufacturer.group(1) == 'Novatek':
                    srvr.close()
                    clnt.close()
                    return True

            time.sleep(1)

        srvr.close()
        clnt.close()
        return False

    def connect(self):
        if self.ip is None:
            if not self.find_tcl_tv():
                raise RuntimeError("TCL TV not found on the network")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.ip, self.port))
        self.start_keep_alive()

    def start_keep_alive(self):
        if self.client_socket is not None:
            self.client_socket.send('nop'.encode('utf-8'))
            self.client_socket.recv(2048)
            threading.Timer(20.0, self.start_keep_alive).start()

    def close(self):
        if self.client_socket:
            self.client_socket.close()

    def keypress(self, key):
        if not self.client_socket:
            raise RuntimeError("Not connected to TCL TV")

        data = (
            '<?xml version="1.0" encoding="utf-8"?>'
            f'<root><action name="setKey" eventAction="{key}" keyCode="{key}" /></root>'
        )

        self.client_socket.send(data.encode())