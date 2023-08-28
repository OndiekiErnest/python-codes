__author__ = "ondieki.codes@gmail.com"

import socket
import threading
from struct import pack, unpack


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


def pad_message(msg: str, msg_type="str") -> bytes:
    """
        Pack strings for transfer (>QI == 12 bytes)
        Used for strings only
    """
    msg_type = msg_type.encode()
    msg_length = len(msg.encode())
    padded = pack(">QI", msg_length, len(msg_type))
    # return bytes
    return padded


def receive_all(sock: socket.socket, n: int) -> bytearray:
    """
        recv n bytes of strings; return None on EOF
    """
    data = bytearray()
    while len(data) < n:
        to_read = n - len(data)
        packet = sock.recv(
            BUFFER if to_read > BUFFER else to_read)
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
            self.server_socket.listen(5)
            print(f'[LISTENING] : {self.server_socket.getsockname()}')

            while True:

                # Accept client connection
                client_connection, address = self.server_socket.accept()
                print("CONNECTION:")
                msg = client_connection.recv(1024)
                msg = msg.decode()
                parser = parse_message.Parser(msg)
                user, _ = parser.parse()
                # Avoid having two usernames at the same time
                if is_taken(user):
                    to_send = f"[Username {user} is already taken!]"
                    lengths = pad_message(to_send)
                    client_connection.sendall(lengths)
                    client_connection.sendall("str".encode())
                    client_connection.sendall(to_send.encode())
                    client_connection.close()
                else:
                    print("[CONNECTION] :", user)
                    # tell the connected of a new user
                    lengths = pad_message(msg)
                    send(lengths, "str", msg, client_connection)
                    # Add client connection to connections list
                    session = _Session(client_connection, user, address)
                    connections.append(session)
                    # minus client_connection
                    to_send = f"[{len(connections)-1} online]"
                    lengths = pad_message(to_send)
                    send(lengths, "str", to_send, client_connection)
                    try:
                        # minus receiver (client_connection)
                        to_send = f"[{len(connections)-1} online]"
                        lengths = pad_message(to_send)
                        client_connection.sendall(lengths)
                        client_connection.sendall("str".encode())
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
                    remove_connection(conn)

            self.server_socket.close()

    def handle_user_connection(self, connection: _Session) -> None:
        '''
            Keep user connection alive in order to keep receiving their messages
        '''
        while True:
            print("GOT HERE!")
            try:

                # If no message is received, there is a chance that connection has ended
                # so in this case, we need to close connection and remove it from connections list.
                first_msg = connection.socket.recv(12)
                if first_msg:
                    # Get client message
                    msg_length, ext_length = unpack(">QI", first_msg)
                    sec_msg = connection.socket.recv(ext_length)
                    extension = unpack(f"{ext_length}s", sec_msg)[0].decode()
                    if extension == "str":
                        # handle text messages here
                        msg = receive_all(connection.socket, msg_length)
                        # Log message sent by user, 'replace' errors for terminal print
                        print(f'[MESSAGE] : {msg.decode("utf-8","replace")}')

                        # broadcast to users connected to server
                        send(first_msg, extension,
                             msg.decode(), connection.socket)

                    else:
                        # handle files here; we will save the files first then send notifications of new files
                        online = connections
                        print('[MESSAGE] : File')
                        msg = connection.socket.recv(BUFFER)
                        send(first_msg, extension, msg, connection.socket)
                        while 1:
                            # receive as we send for memory sake
                            msg = connection.socket.recv(BUFFER)
                            if msg:
                                broadcast(msg, connection.socket,
                                          list_connections=online)
                            else:
                                break
                        # I don't know why when I omit the line below, the receiver hangs
                        broadcast(msg, connection.socket)

                # Close connection if no message was sent/received
                else:
                    print(f"[DISCONNECTION] : {connection.username}")
                    to_send = f'{connection.username} went offline!'
                    lengths = pad_message(to_send)
                    send(lengths, "str", to_send, connection.socket)
                    remove_connection(connection)
                    break

            except Exception as e:
                # print(f'Error handling user connection: {e}')
                # pad message that are originating from only the server
                print(f"[DISCONNECTION] : {e}")
                to_send = f'{connection.username} went offline!'
                lengths = pad_message(to_send)
                send(lengths, "str", to_send, connection.socket)
                # minus 2; one who left and the receiver
                to_send = f"[{len(connections)-2} online]"
                lengths = pad_message(to_send)
                send(lengths, "str", to_send, connection.socket)
                remove_connection(connection)
                break

    def broadcast(message: bytes, connection: socket.socket, list_connections=connections) -> None:
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
                    remove_connection(client_conn)

    def send(lengths: bytes, msg_type: str, msg: str, conn: socket.socket) -> None:
        broadcast(lengths, conn)
        ext = pack(f"{len(msg_type.encode())}s", msg_type.encode())
        broadcast(ext, conn)
        if msg_type == "str":
            broadcast(msg.encode(), conn)
        # if it's a file
        else:
            broadcast(msg, conn)

    def remove_connection(conn: _Session) -> None:
        '''
            Remove specified Session from connections list
        '''

        # Check if Session exists on connections list
        if conn in connections:
            # Close socket connection and remove Session from connections list
            conn.socket.close()
            connections.remove(conn)


if __name__ == "__main__":
    server()
