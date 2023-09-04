__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

import socket
import threading
import os
from pyftpdlib.authorizers import DummyAuthorizer, WindowsAuthorizer
from pyftpdlib.handlers import FTPHandler, DTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
import logging
import parse_message


# Global variable that mantains client's connections
# we will need to store this to a file for later use
connections = []


class _Session():
    """
        Store information about the clients
    """
    __slots__ = "socket", "username", "address"

    def __init__(self, connection: socket.socket, user: str, addr: str):
        self.socket = connection
        self.username = user
        self.address = addr


def len_bytes(msg: str) -> bytes:
    """
        get the length of the msg and return it in bytes
    """

    size = 12
    length = str(len(msg))
    by = size - len(length)
    padding = "j" * by
    byte_str = length + padding
    return byte_str.encode()


def receive_all(sock: socket.socket, n: int) -> bytearray:
    """
        recv n bytes of strings; return None on EOF
    """
    data = bytearray()
    while len(data) < n:
        to_read = n - len(data)
        packet = sock.recv(
            1024 if to_read > 1024 else to_read)
        data.extend(packet)
    return data


def is_taken(new_user: str) -> bool:
    # check username and return true if found
    for user in connections:
        if new_user == user.username:
            return True
            break
    return False


class Server():

    def __init__(self):
        '''
            receive client's connections and start a new thread
            to handle their messages
        '''

        LISTENING_PORT = 12000
        SERVER = socket.gethostbyname(socket.gethostname())

        try:
            # Create server instance
            self.server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("", LISTENING_PORT))
            self.server_socket.listen(12)
            print(f'[LISTENING] : {self.server_socket.getsockname()}')
            ftp_thread = threading.Thread(target=self.start_FTP,
                                          args=(SERVER,), name="FTP")
            ftp_thread.daemon = True
            ftp_thread.start()

            while True:

                # Accept client connection
                client_connection, address = self.server_socket.accept()
                msg = client_connection.recv(1024)
                msg = msg.decode()
                parser = parse_message.Parser(msg)
                user, _ = parser.parse()
                # Avoid having two usernames at the same time
                if is_taken(user):
                    to_send = f"[Username {user} is already taken!]"
                    length = len_bytes(to_send)
                    client_connection.sendall(length)
                    client_connection.sendall(to_send.encode())
                    client_connection.close()
                else:
                    print("[CONNECTION] :", user)
                    # tell the connected of a new user
                    length = len_bytes(msg)
                    self.send(length, msg, client_connection)
                    # Add client connection to connections list
                    session = _Session(client_connection, user, address)
                    connections.append(session)
                    # minus client_connection
                    to_send = f"[{len(connections)-1} online]"
                    length = len_bytes(to_send)
                    self.send(length, to_send, client_connection)
                    try:
                        # minus receiver (client_connection)
                        to_send = f"[{len(connections)-1} online]"
                        length = len_bytes(to_send)
                        client_connection.sendall(length)
                        client_connection.sendall(to_send.encode())
                    except Exception as e:
                        print("[Error Sending online list] :", e)
                    # Start a new thread to handle client connection and receive it's messages
                    # in order to send to others connections
                    user_thread = threading.Thread(target=self.handle_user_connection, args=(
                        session,), name=user)
                    user_thread.daemon = True
                    user_thread.start()

        except Exception as e:
            print(f'[Error has occurred when instancing socket] : {e}')
        finally:
            # In case of any problem we clean all connections and close the server connection
            if len(connections) > 0:
                for conn in connections:
                    self.remove_connection(conn)

            self.server_socket.close()

    def handle_user_connection(self, connection: _Session) -> None:
        '''
            Keep user connection alive in order to keep receiving their messages
        '''
        while True:
            try:

                # If no message is received, there is a chance that connection has ended
                # so in this case, we need to close connection and remove it from connections list.
                first_msg = connection.socket.recv(12)
                if first_msg:
                    # Get client message
                    msg_length = int(first_msg.decode().strip("j"))
                    # handle text messages here
                    msg = receive_all(connection.socket, msg_length)
                    # Log message sent by user, 'replace' errors for terminal print
                    print(f'[MESSAGE] : {msg.decode("utf-8","replace")}')

                    # broadcast to users connected to server
                    self.send(first_msg, msg.decode(), connection.socket)

                # Close connection if no message was sent/received
                else:
                    print(f"[DISCONNECTION] : {connection.username}")
                    to_send = f'{connection.username} went offline!'
                    length = len_bytes(to_send)
                    self.send(length, to_send, connection.socket)
                    self.remove_connection(connection)
                    break

            except Exception as e:
                # print(f'Error handling user connection: {e}')
                # pad message that are originating from only the server
                print(f"[DISCONNECTION] : {e}")
                to_send = f'{connection.username} went offline!'
                length = len_bytes(to_send)
                self.send(length, to_send, connection.socket)
                # minus 2; one who left and the receiver
                to_send = f"[{len(connections)-2} online]"
                length = len_bytes(to_send)
                self.send(length, to_send, connection.socket)
                self.remove_connection(connection)
                break

    def broadcast(self, message: bytes, connection: socket.socket, list_connections=connections) -> None:
        '''
            Broadcast message to all users connected to the server
        '''

        # Iterate on connections in order to send message to all client's connected
        for client_conn in list_connections:
            # Check if it isn't the connection of the sender
            if client_conn.socket != connection:
                try:
                    # Sending message to client connection; sendall is blocking
                    client_conn.socket.sendall(message)

                # if it fails, there is a chance of socket has died
                except Exception as e:
                    print(f'[Error broadcasting message] : {e}')
                    self.remove_connection(client_conn)

    def send(self, length: bytes, msg: str, conn: socket.socket) -> None:
        self.broadcast(length, conn)
        self.broadcast(msg.encode(), conn)

    def remove_connection(self, conn: _Session) -> None:
        '''
            Remove specified Session from connections list
        '''

        # Check if Session exists on connections list
        if conn in connections:
            # Close socket connection and remove Session from connections list
            conn.socket.close()
            connections.remove(conn)

    def start_FTP(self, ip):
        try:
            authorizer = DummyAuthorizer()
            authorizer.add_anonymous("C:\\Users\\code\\Music\\Playlists",
                                     msg_login="Connection",
                                     msg_quit="Disconnection")
            self.throttled_handler = ThrottledDTPHandler
            # kbps
            self.throttled_handler.read_limit = 1024 * 1024
            self.throttled_handler.write_limit = 1024 * 1024

            self.handler = FTPHandler
            self.handler.use_gmt_times = False
            self.handler.authorizer = authorizer
            self.handler.dtp_handler = self.throttled_handler

            # logging.basicConfig(filename="data\\debug.log", level=logging.DEBUG)

            self.ftp_server = FTPServer((ip, 21), self.handler)
            self.ftp_server.serve_forever()
        except Exception:
            print("[Error starting FTP connection]")


if __name__ == "__main__":
    Server()
