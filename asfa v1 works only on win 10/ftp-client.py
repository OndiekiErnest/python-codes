from ftplib import FTP
import os
import datetime

output_folder = "data"


if __name__ == '__main__':
    ftp_client = FTP()
    # ftp_client.set_debuglevel(2)
    ftp_client.connect("127.0.0.1", 21)
    # ftp_client.login("Ernesto", "12345")
    ftp_client.login()
    print("Logged in!")
    print("\nFiles:\n\n")
    for file in ftp_client.nlst():
        print(file)
