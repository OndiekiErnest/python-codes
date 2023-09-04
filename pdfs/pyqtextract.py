from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
    QPushButton,
    QApplication,
    QFrame,
)
from PyQt6.QtCore import (
    Qt,
)
import os
import fitz
import imviewer
import pandas as pd
from extracttables import parse_table


class CtrlsPane(QFrame):
    """ custom frame with widgets """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.preview_btn = QPushButton("Preview")
        # add to layout
        self.main_layout.addWidget(self.preview_btn)


class PreviewPane(QFrame):
    """ custom frame with previewing widgets """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MainWin(QWidget):
    """ custom main application widget """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(900, 480)

        self.main_layout = QHBoxLayout(self)
        self.currentpage_no = 23
        # widgets
        self.ctrls = CtrlsPane()
        self.pdfviewer = imviewer.ImageViewer()
        self.previewer = PreviewPane()
        # add to layout
        self.main_layout.addWidget(self.ctrls)
        self.main_layout.addWidget(self.pdfviewer)
        self.main_layout.addWidget(self.previewer)
        # bind signals
        self.ctrls.preview_btn.clicked.connect(self.gettable_data)

    def browse_pdf(self):
        """ open filedialog and select pdf """
        filename = QFileDialog.getOpenFileName(
            self,
            caption="Choose PDF file",
            directory=os.path.expanduser(os.path.join("~", "Downloads")),
            filter="PDF (*.pdf);;XPS (*.xps);;OXPS (*.oxps);;EPUB (*.epub);;CBZ (*.cbz)",
        )[0]
        if filename:
            # create fitz doc
            self.pdf_doc = fitz.Document(filename)
            self.total_pages = self.pdf_doc.page_count
            self.display_page(self.currentpage_no)

    def _get_pdf_pix(self, page_no: int):
        """ create and return pdf pixmap """
        page = self.pdf_doc[page_no]
        return page.get_pixmap(annots=False, dpi=192)

    def gettable_data(self):
        """ get data, create dataframe, preview """
        bbox = self.pdfviewer.get_bbox()
        cols = self.pdfviewer.get_cols()
        print(cols)
        page = self.pdf_doc[self.currentpage_no]
        # extact data
        table_data = parse_table(page, bbox, columns=cols)
        self.table_df = pd.DataFrame(data=table_data)
        # print(self.table_df)

    def save_as(self, as_type="csv"):
        """ save-as functionality """

    def draw_rect(self):
        """ draw rect, remove old one """

    def add_column(self):
        """ add column to already created table """

    def display_page(self, page_no: int):
        """ display page number """
        # page_no = page_no - 1
        pix = self._get_pdf_pix(page_no)
        # display
        self.pdfviewer.set_pix(pix)

    def next_page(self):
        """ increment page counter and call display_page """
        self.currentpage_no += 1
        self.currentpage_no = min(self.currentpage_no, self.total_pages)
        self.display_page(self.currentpage_no)

    def previous_page(self):
        """ decrement page counter and call display_page """
        self.currentpage_no -= 1
        self.currentpage_no = max(1, self.currentpage_no)
        self.display_page(self.currentpage_no)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWin()
    window.showMaximized()
    window.browse_pdf()

    sys.exit(app.exec())
