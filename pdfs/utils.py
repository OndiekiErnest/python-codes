__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"
__dated__ = "12-09-22"  # DDMMYY

from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator

from openpyxl import Workbook
from openpyxl.styles import Alignment

import re


EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

# REGEX = r"[\w\.-]+@[\w\.-]+\.\w+"

# import chardet
# rawdata = open(file, "r").read()
# result = chardet.detect(rawdata)
# charenc = result['encoding']


def getTextBbox(filename):
    """ open 'filename' pdf and yield text and its bounding box """
    with open(filename, 'rb') as fp:
        resource_manager = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(resource_manager, laparams=laparams)
        interpreter = PDFPageInterpreter(resource_manager, device)
        # get the first page
        pages = PDFPage.get_pages(fp, maxpages=1, check_extractable=True)

        for page in pages:
            # process page
            interpreter.process_page(page)
            # get page layout
            layout = device.get_result()
            for lobj in layout:
                # if layout object is of LTTextBoxHorizontal instance
                if isinstance(lobj, LTTextBoxHorizontal):
                    # yield text and its bonding box (left, bottom, right, top = lobj.bbox)
                    yield lobj.get_text(), (lobj.bbox[0], lobj.bbox[3])


def getInvoiceNum(txt):
    """ split txt on space and hash (to be safe); return invc num """
    spl = re.split("[ #\n]", txt)
    # remove empty items
    empty_removed = [t for t in spl if t]
    # return the invoice number
    return empty_removed[1]


def getEmail(string):
    """ search, return email address or return an empty str """
    match = re.search(EMAIL_REGEX, string)
    if match:
        return match.group(0)
    return ""


def getName(string):
    """ get name from string (first line) """
    # split on newlines and get the first line
    spl_str = string.split("\n")[0]
    # strip any spaces
    return spl_str.strip()


class XLWriter(Workbook):
    """ subclass of openpyxl Workbook """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_data(self, cell: str, data: str, wrapText=None):
        """ add data to a cell (A1) """
        self.active[cell].value = data
        if wrapText:
            self.active[cell].alignment = Alignment(wrapText=True)
