__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"

import os
from struct import unpack
import socket
from datetime import datetime

# class Attach():

#     def __init__(self):
#         self.data = None
#         self.initialdir = os.path.expanduser("~\\Documents")

#     def choose_file(self, tk_askfile):

#         self.file = tk_askfile(title="Attach file",
#                                filetypes=(("All files", "."),),
#                                initialdir=self.initialdir)
#         self.initialdir = os.path.dirname(self.file)

#     def read(self, file):
#         file_size = os.path.getsize(file)
#         with open(file, "rb") as file:
#             data = file.read().encode()
#             self.data = struct.pack(">I", file_size,
#                                     os.path.basename(file)) + data
#             return self.data

#     def receive(self):
#         pass

class ServerProtocol():

    def __init__(self):
        self.socket = None
        self.dst_dir = os.path.expanduser("~\\Downloads")

    def listen(self, server_ip, server_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((server_ip, server_port))
        self.socket.listen(1)
        print("[LISTENING...]")

    def handle_file(self):
        try:
            while True:
                socket_connection, address = self.socket.accept()
                try:
                    first_msg = socket_connection.recv(12)
                    length, ext_size = unpack(">QI", first_msg)
                    sec_msg = socket_connection.recv(ext_size)
                    extension = unpack(f"{ext_size}s", sec_msg)[0]
                    data = bytearray()
                    while len(data) < length:
                        to_read = length - len(data)
                        packet = socket_connection.recv(
                            16384 if to_read > 16384 else to_read)
                        data.extend(packet)
                    # send confirmation back
                    confirmation = b'0'
                    assert len(confirmation) == 1
                    socket_connection.send(confirmation)
                finally:
                    socket_connection.close()
                with open(os.path.join(self.dst_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S%f')}.{extension.decode()}"), "wb") as file:
                    file.write(data)
        finally:
            self.close()

    def close(self):
        self.socket.close()
        self.socket = None


if __name__ == '__main__':
    server = ServerProtocol()
    server.listen('', 6000)
    server.handle_file()
