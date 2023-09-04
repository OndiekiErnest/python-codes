import fitz


def block_sort(block: tuple):
    """ sort block according to coordinates """

    # (x0, y0, x1, y1, "lines in the block", block_no, block_type)

    x0, y0, x1, y1, text, b_no, b_type = block
    return y0, x0


def only_text(block: tuple):
    """ return only texts from block """
    return block[4]


def is_image(block: tuple):
    """ return True if block_type is 1 """
    return block[6] == 1


def is_text(block: tuple):
    """ return True if block_type is 0 """
    return block[6] == 0


if __name__ == "__main__":
    fname = r"C:\Users\Windows 10 Pro\Desktop\Codes\Raj\Northern-Video-HDMIEXTC6-Cable-Assembly-Features-Specifications.pdf"
    d_fname = r"C:\Users\Windows 10 Pro\Downloads\aparici-corten-1.pdf"
    doc = fitz.Document(d_fname)  # open document

    for page in doc:  # iterate the document pages
        for block in sorted(page.get_text("blocks"), key=block_sort):
            if is_text(block):
                # process text
                print(only_text(block))
            elif is_image(block):
                # process image
                print("\n")  # print new line for now
