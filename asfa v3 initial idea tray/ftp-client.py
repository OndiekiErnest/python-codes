from ftplib import FTP

output_folder = "data"


if __name__ == '__main__':
    ftp_client = FTP()
    # ftp_client.set_debuglevel(2)
    ftp_client.connect("127.0.0.1", 21)
    ftp_client.login()
    print("Logged in!")
    print("\nFiles:\n\n")
    lst = []
    ftp_client.dir(lst.append)
    for item in lst:
        lst = item.split()
        name, size = item[55:], lst[4]
        print(name, size)
    ftp_client.quit()
    x = input("Done?")
