# remove line number and space

def read_py(filename):
    """ read and yield line """
    with open(filename, "rb") as py_file:
        for line in py_file.readlines():
            yield line


def parse_line(line: str):
    """ parse and return parsed line """
    sp_line = line.split(b" ")  # split on space
    return b" ".join(sp_line[1:])


def write_py(from_, to):
    """ format and write lines """
    parser = parse_line
    with open(to, "wb") as py_file:
        for line in read_py(from_):
            py_file.write(parser(line))
            # print(parser(line))


if __name__ == '__main__':
    write_py("tkvlc.py", "tkvlcf.py")
