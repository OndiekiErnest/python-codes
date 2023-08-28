from struct import pack
import socket
import pkgutil
import os
import encodings

class ClientProtocol():

    def __init__(self):
        self.socket = None

    def connect(self, server_ip: str, server_port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, server_port))

    def send_file(self, file_data: bytes, file_ext: str) -> bool:

        file_ext = file_ext.encode()
        # use struct for consistence
        lengths = pack(">QI", len(file_data), len(file_ext))
        ext = pack(f"{len(file_ext)}s", file_ext)

        # sendall to make sure it blocks
        self.socket.sendall(lengths)
        self.socket.sendall(ext)
        self.socket.sendall(file_data)
        confirmation = self.socket.recv(1)
        return confirmation.decode() == '0'

    def close(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
        self.socket = None
        
def all_encodings():
    modnames = set(
                    [modname for importer, modname, ispkg in pkgutil.walk_packages(
                        path=[os.path.dirname(encodings.__file__)], prefix="")])
    aka = set(encodings.aliases.aliases.values())
    return modnames.union(aka)


if __name__ == '__main__':

    client = ClientProtocol()
    client.connect("127.0.0.1", 6000)
    sent = client.send_file(b"pass-file-data(open in rb mode)", "txt")
    print("Sent:", sent)
    client.close()
