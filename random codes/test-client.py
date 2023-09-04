
__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

from ftplib import FTP
from datetime import datetime
import sys
import threading
import socket
import os
import time


class Client():

    def __init__(self, username, **kwargs):
        self.user = username
        # on clicking attach, open Documents folder first
        self.initialdir = os.path.expanduser("~\\Documents")
        # instantiate online users to 0
        self.online_users = "0 online"

        self.SERVER_ADDRESS = kwargs.get("server_addr", "127.0.0.1")
        self.SERVER_PORT = kwargs.get("server_port", 12000)

        # Instantiate socket and start connection with server
        self.socket_instance = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.socket_instance.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # start FTP client
        self.ftp_client = FTP()
        try:
            print(self.SERVER_ADDRESS, "->", self.SERVER_PORT)
            self.socket_instance.connect((self.SERVER_ADDRESS,
                                          self.SERVER_PORT))
            # this is padded on the server after checking username; no need to pad with its length
            self.socket_instance.sendall(f"{self.user} is online!".encode())
            print(f"{self.user} online!")
        except Exception as e:
            print("[Client init Error] :", e)
            self.socket_instance.close()
        try:
            # Create a thread in order to handle messages sent by server
            self.client_thread = threading.Thread(target=self.handle_messages,
                                                  args=(self.socket_instance,))
            self.client_thread.start()

        except Exception as e:
            print(f'[Client Error] : {e}')
            self.socket_instance.close()

    def _from_clipborad(self, event=None):
        """
            Get clipboard content and paste on cursor position
        """
        pass

    def sendall(self, length: bytes, msg: bytes) -> None:
        try:
            self.socket_instance.sendall(length)
            self.socket_instance.sendall(msg)
        except Exception as e:
            print("[Error Sending] :", e)

    def receive_all(self, sock: socket.socket, n: int) -> bytearray:
        """
            recv n string bytes; return bytearray of received
        """
        data = bytearray()
        while len(data) < n:
            to_read = n - len(data)
            packet = sock.recv(
                1024 if to_read > 1024 else to_read)
            data.extend(packet)
        return data

    def len_bytes(self, msg: str) -> bytes:
        # get the msg length and encode it

        size = 12
        length = str(len(msg))
        by = size - len(length)
        padding = "j" * by
        byte_str = length + padding
        return byte_str.encode()

    def send_file(self, file):

        # self.ftp_client.set_debuglevel(2)
        self.ftp_client.connect("127.0.0.1", 21)
        # self.ftp_client.login("Ernesto", "12345")
        self.ftp_client.login()
        print("\nFiles:\n\n")
        for file in self.ftp_client.nlst():
            print(file)

    def handle_messages(self, connection: socket.socket):
        """
            Receive messages sent by the server and display them to user
            Threaded
        """

        while True:
            try:
                # receive the string that was packed and unpack
                # If there is no message, there is a chance that connection has closed
                # so the connection will be closed and an error will be displayed.
                # If not, it will try to decode message in order to show to user.
                first_msg = connection.recv(12)
                if first_msg:
                    msg_length = int(first_msg.decode().strip("j"))

                    msg = self.receive_all(connection, msg_length).decode()
                    # receive server message for online users
                    if msg.startswith("[") and msg.endswith("online]"):
                        # update the online list
                        self.online_users = msg[1:-1]
                        print(self.online_users)
                    # get notified if username taken
                    elif msg.startswith("[Username") and msg.endswith("taken!]"):
                        # handle username taken error
                        print(msg)
                    # if it's a message from another client
                    else:
                        # handle incoming message
                        print("MESSAGE -> ", msg)

                else:
                    print('[Error server cannot respond]')
                    print("Server is down!")
                    connection.close()
                    break

            except Exception as e:
                print(f'[Error Handling Message] : {e}')
                print("Server is down!")
                connection.close()
                break

    def client_response(self, msg) -> None:
        """
            Read user's input; close connection if there's an error
        """

        try:
            # Get typed text
            # Skip if nothing has been typed or contains only spaces or status is not good

            # handle not sent, outgoing
            # Parse message to utf-8
            length = self.len_bytes(msg)
            self.sendall(length, msg.encode())
        except Exception as e:
            print("[Error sending] :", e)

    def kill(self) -> None:
        # killing while sending in progress will make
        # the server and receiver clients hang in while loop;
        # incomplete files will be saved
        pass


if len(sys.argv) < 2:
    # restrict the len of the username
    print("Usage: > main.py <Username>")
else:
    myip = socket.gethostbyname(socket.gethostname())
    try:
        chat_instance = Client(sys.argv[1])

    except Exception:
        chat_instance = Client(sys.argv[1], server_addr=myip)
