from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LAParams
from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

fname = r"C:\Users\Windows 10 Pro\Desktop\Codes\Raj\Northern-Video-HDMIEXTC6-Cable-Assembly-Features-Specifications.pdf"
# for page_layout in extract_pages(fname):
#     for element in page_layout:
#         if isinstance(element, LTTextContainer):
#             print(element.get_text())


output_string = StringIO()
with open(fname, 'rb') as in_file:
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    params = LAParams(line_overlap=0.2,
                      char_margin=2.0,
                      line_margin=0.2,
                      word_margin=0.1,
                      boxes_flow=-1.0,
                      detect_vertical=False,
                      all_texts=False)
    device = TextConverter(rsrcmgr, output_string, laparams=params)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

print(output_string.getvalue())  # does not respect reading-order layout
