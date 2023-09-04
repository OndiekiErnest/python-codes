""" modify PDF author and title inplace """

from pdfrw import PdfReader, PdfWriter


def modifyPDF(filename: str, author: str, title: str):
    """ change filename's author and title """

    trailer = PdfReader(filename)
    trailer.Info.Title = title
    trailer.Info.Author = author

    pdf_writer = PdfWriter()
    pdf_writer.trailer = trailer
    pdf_writer.write(filename)
