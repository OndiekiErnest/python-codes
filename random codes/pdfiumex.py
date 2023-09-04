# pdf examples
# import fitz
pdf_file = r"C:\Users\Windows 10 Pro\Desktop\Codes\Raj\Northern-Video-N2NVR8POE-Hdmi-Vga-Features-Specifications.pdf"
pdf_file1 = r"C:\Users\Windows 10 Pro\Desktop\Codes\Raj\Northern-NPP5E12PM-Patch-Panel-Features-Specifications.pdf"
pdf_file2 = r"C:\Users\Windows 10 Pro\Desktop\Codes\Raj\Northern-Video-HDMIEXTC6-Cable-Assembly-Features-Specifications.pdf"
# out_file = "C:\\Users\\Windows 10 Pro\\Downloads\\fitz 1.html"
# file_obj = open(out_file, "wb")

# with fitz.Document(r"C:\Users\Windows 10 Pro\Desktop\Codes\Raj\Northern-Video-N2NVR8POE-Hdmi-Vga-Features-Specifications.pdf") as doc:
#     # print("Outline:", doc.outline)
#     # loop through pages
#     # page = doc.load_page(1)
#     x_spaces = fitz.TEXT_INHIBIT_SPACES
#     e_l = fitz.TEXT_PRESERVE_LIGATURES
#     e_sp = fitz.TEXT_PRESERVE_SPANS
#     e_ws = fitz.TEXT_PRESERVE_WHITESPACE
#     txt_flags = x_spaces | e_l | e_sp | e_ws
#     for page in doc:
#         text = page.get_text("html").encode("utf8")  # get plain text (is in UTF-8)
#         file_obj.write(text)  # write text of page

# file_obj.close()
import pypdfium2 as pdfium


def pdfium_extract_text(filename):
    """ extract text from PDF file """
    pdf = pdfium.PdfDocument(filename)
    version = pdf.get_version()  # get the PDF standard version
    n_pages = len(pdf)  # get the number of pages in the document

    print("PDF Version:", version)
    print("PAGES:", n_pages, "\n\n")

    for page in pdf:

        # Load a text page helper
        textpage = page.get_textpage()

        # Extract text from the whole page
        yield textpage.get_text_range()

# image = page.render_to(
#     pdfium.BitmapConv.pil_image,
#     scale=1,                           # 72dpi resolution
#     rotation=0,                        # no additional rotation
#     crop=(0, 0, 0, 0),                 # no crop (form: left, right, bottom, top)
#     greyscale=False,                   # coloured output
#     fill_colour=(255, 255, 255, 255),  # fill bitmap with white background before rendering (form: RGBA)
#     colour_scheme=None,                # no custom colour scheme
#     optimise_mode=pdfium.OptimiseMode.NONE,   # no optimisations (e. g. subpixel rendering)
#     draw_annots=True,                  # show annotations
#     draw_forms=True,                   # show forms
#     no_smoothtext=False,               # anti-alias text
#     no_smoothimage=False,              # anti-alias images
#     no_smoothpath=False,               # anti-alias paths
#     force_halftone=False,              # don't force halftone for image stretching
#     rev_byteorder=False,               # don't reverse byte order
#     prefer_bgrx=False,                 # don't prefer four channels for coloured output
#     force_bitmap_format=None,          # don't force a specific bitmap format
#     extra_flags=0,                     # no extra flags
#     allocator=None,                    # no custom allocator
#     memory_limit=2**30,                # maximum allocation (1 GiB)
# )
# image.show()


if __name__ == '__main__':

    import os
    pdfs = (pdf_file, pdf_file1, pdf_file2)
    for filename in pdfs:
        name, _ = os.path.splitext(filename)
        # out_file = f"{name}.txt"
        # with open(out_file, "wb") as output:
        for page_txt in pdfium_extract_text(filename):
            print(page_txt)
            # output.write(page_txt.encode("utf-8"))
