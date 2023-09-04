from PyQt6.QtCore import (
    Qt,
    QPoint,
    QRect,
    QTimer,
    QSize,
)
from PyQt6.QtGui import (
    QPixmap, QPainter,
    QIcon,
)
from PyQt6.QtPrintSupport import (
    QPrintDialog, QPrinter,
)
from PyQt6.QtWidgets import (
    QLabel, QSizePolicy,
    QScrollArea,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QFrame,
)
from os.path import (
    expanduser,
    join,
)
import images
import fitz


def create_icon(data: bytes) -> QIcon:
    """ create and return a QIcon from data """
    pix = QPixmap()
    pix.loadFromData(data)
    return QIcon(pix)


class SHFrame(QFrame):
    """ hiding and showing custom frame """

    def __init__(self, hide_timer: QTimer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("btnsframe")

        self.hide_timer = hide_timer
        self.previous_cursor = self.cursor()

    def enterEvent(self, event):
        """ on cursor enter event """
        self.hide_timer.stop()
        self.previous_cursor = self.cursor()
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """ on cursor leave event """
        self.hide_timer.start()
        self.setCursor(self.previous_cursor)
        super().leaveEvent(event)


class PDFArea(QLabel):
    """ custom QLabel to render PDF page bitmap """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # center horizonatally
        self.setMouseTracking(True)  # get cursor pos in realtime

        self.rect_begin = QPoint()
        self.rect_end = QPoint()
        self.rect_w = 0
        self.rect_h = 0
        self.added_cols = []
        self.current_scale = 0.38
        self.default_scale = 0.38

        self.page_pix = QPixmap()
        # flags
        self.mouse_pressed = False

    def add_pix(self, pixmap: fitz.Pixmap):
        """ create image from qpixmap """
        self.pdf_pix = pixmap  # fitz pixmap copy for refreshing display
        self.page_pix.loadFromData(pixmap.tobytes())
        self.setPixmap(self.page_pix)

    def _draw_rectangle(self):
        """ draw table, rect and cols """
        painter = QPainter(self)
        if not (self.rect_begin.isNull() and self.rect_end.isNull()):
            rect = QRect(self.rect_begin, self.rect_end)  # create rect in QLabel
            painter.drawRect(rect.normalized())
            # draw cols
            for pos in self.added_cols:
                painter.drawLine(
                    pos.x(),  # x1
                    self.rect_begin.y(),  # y1
                    pos.x(),  # x2
                    self.rect_end.y()  # y2
                )
        painter.end()

    def resize(self, scale):
        """ resize label/image, and clear the table """
        self.current_scale = scale
        # clear table
        self.rect_begin, self.rect_end = QPoint(), QPoint()
        self.added_cols.clear()
        # resize label
        super().resize(scale * self.pixmap().size())
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        self._draw_rectangle()

    def mouseMoveEvent(self, event):
        """ extends mouse move functionality """
        super().mouseMoveEvent(event)
        c_pos = event.pos()

        if self.current_scale == self.default_scale:
            if self.mouse_pressed:
                self.rect_end = c_pos
                self.update()
                # get rect height and width
                # self.rect_h = abs(self.rect_end.y() - self.rect_begin.y())
                # self.rect_w = abs(self.rect_end.x() - self.rect_begin.x())

            # if cursor in rect
            if self._cursor_in_rect(c_pos):
                # change cursor
                self.setCursor(Qt.CursorShape.SplitHCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
            # if self._cursor_on_rect(c_pos):
                # move rect
                # self.setCursor(Qt.CursorShape.SizeAllCursor)

    def mousePressEvent(self, event):
        """ extends mouse press functionality """
        super().mousePressEvent(event)
        c_pos = event.pos()

        if self.current_scale == self.default_scale:
            if self._cursor_in_rect(c_pos):
                # draw column
                self.added_cols.append(c_pos)
                self.update()
            # elif self._cursor_on_rect(c_pos):
            #     pass
            else:
                # upadet flag only when clicked outside rect
                self.mouse_pressed = True
                # clear cols set
                self.added_cols.clear()
                # start, end of rect
                self.rect_begin = c_pos
                self.rect_end = c_pos
                self.update()
                self.add_pix(self.pdf_pix)  # refresh display

    def mouseReleaseEvent(self, event):
        """ extends mouse release functionality """
        super().mouseReleaseEvent(event)

        self.mouse_pressed = False

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.current_scale == self.default_scale:
            self.setCursor(Qt.CursorShape.CrossCursor)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.current_scale == self.default_scale:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _cursor_in_rect(self, c_pos):
        """ check if c_pos is in rect """
        d_rect = QRect(self.rect_begin, self.rect_end)
        return d_rect.contains(c_pos)

    def _cursor_on_rect(self, c_pos: QPoint):
        """ check if c_pos is in rect """
        return any(
            (c_pos.x() == self.rect_begin.x(),
             c_pos.y() == self.rect_begin.y(),
             c_pos.x() == self.rect_end.x(),
             c_pos.y() == self.rect_end.y(),
             )
        )

    def get_bbox(self) -> tuple:
        """ """
        return (
            self.rect_begin.x(),
            self.rect_begin.y(),
            self.rect_end.x(),
            self.rect_end.y(),
        )


class Button(QPushButton):
    """ custom button """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFixedSize(30, 20)
        self.setObjectName("viewerBtn")


class ImageViewer(QScrollArea):
    """ image viewer widget """

    __slots__ = (
        "printer",
        "scale_factor",
        "fit_to_win",
        "image_label",
    )

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("viewer")
        self.setMouseTracking(True)

        try:
            self.setWindowIcon(parent.windowIcon())
        except AttributeError:
            pass

        self.scale_factor = 1.0
        self.fit_to_win = False

        self.image_label = PDFArea()
        self.image_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.image_label.setScaledContents(True)

        # center the image label
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # self.setBackgroundRole(QPalette.ColorRole.Dark)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidget(self.image_label)
        self.setVisible(False)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(1)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.hide_timer = QTimer()
        self.hide_timer.setInterval(5000)
        self.hide_timer.timeout.connect(self._hide_btns)
        self.hide_timer.start()

        # create btns
        self._create_buttons()

    def _create_buttons(self):
        """ create control btns """

        self.btns_frame = SHFrame(self.hide_timer)
        frame_layout = QHBoxLayout(self.btns_frame)
        frame_layout.setSpacing(10)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # download, zoom out, zoom in, remove
        self.download_btn = Button()
        self.download_btn.setToolTip("Save")
        self.download_btn.setIcon(create_icon(images.DOWNLOAD_IMG))
        self.download_btn.clicked.connect(self.save_photo)

        self.zoomout_btn = Button()
        self.zoomout_btn.setToolTip("Zoom Out")
        self.zoomout_btn.setIcon(create_icon(images.ZOOMOUT_IMG))
        self.zoomout_btn.clicked.connect(self.zoom_out)

        self.zoomin_btn = Button()
        self.zoomin_btn.setToolTip("Zoom In")
        self.zoomin_btn.setIcon(create_icon(images.ZOOMIN_IMG))
        self.zoomin_btn.clicked.connect(self.zoom_in)

        self.normal_size_btn = Button()
        self.normal_size_btn.setToolTip("Normal")
        self.normal_size_btn.setIcon(create_icon(images.RESTORE_IMG))
        self.normal_size_btn.clicked.connect(self.normal_size)

        self.print_btn = Button()
        self.print_btn.setToolTip("Print")
        self.print_btn.setIcon(create_icon(images.PRINT_IMG))
        self.print_btn.clicked.connect(self.print_photo)

        # map btns
        frame_layout.addWidget(self.download_btn)
        frame_layout.addWidget(self.zoomout_btn)
        frame_layout.addWidget(self.zoomin_btn)
        frame_layout.addWidget(self.normal_size_btn)
        frame_layout.addWidget(self.print_btn)
        # add to main layout
        self.main_layout.addWidget(self.btns_frame)

    def mouseMoveEvent(self, event):
        self._show_btns()
        super().mouseMoveEvent(event)

    def _hide_btns(self):
        """ hide btns """
        self.btns_frame.hide()
        self.hide_timer.stop()

    def _show_btns(self):
        """ show btns """
        self.btns_frame.show()
        self.hide_timer.start()

    def set_pix(self, pixmap: fitz.Pixmap):
        """ on window launch, open image """
        self.image_label.add_pix(pixmap)

        # scroll area visibility
        self.setVisible(True)
        self.normal_size()

    def get_bbox(self):
        """ get drawn table coords and return them """
        return self.image_label.get_bbox()

    def get_cols(self):
        """ get and return col coords """
        return sorted((pos.x() for pos in self.image_label.added_cols))

    def print_photo(self):
        """ print image """
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec():
            painter = QPainter(printer)
            rect = painter.viewport()
            size = self.image_label.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image_label.pixmap().rect())
            painter.drawPixmap(0, 0, self.image_label.pixmap())

    def save_photo(self):
        """ save pixmap to a file """
        fil = "Photos (*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG);;PNG (*.png *.PNG);;JPG (*.jpg *.jpeg *.JPG *.JPEG)"
        filename = QFileDialog.getSaveFileName(self,
                                               caption="Save As...",
                                               filter=fil,
                                               initialFilter="PNG (*.png)",
                                               directory=expanduser(join("~", "Pictures"))
                                               )[0]  # get the first element
        if filename:
            pix = self.image_label.pixmap()
            pix.save(filename)

    def zoom_in(self):
        # if self.scale_factor < 3.0:  # no zooming beyond this
        self.scale_image(1.05)  # scale by factor
        self.normal_size_btn.setEnabled(True)
        # self.zoomout_btn.setEnabled(True)
        # else:
        #     self.zoomin_btn.setDisabled(True)
        #     self.zoomout_btn.setEnabled(True)

    def zoom_out(self):
        # if self.scale_factor > 0.333:  # no zooming below this value
        self.scale_image(0.95)  # scale by factor
        self.normal_size_btn.setEnabled(True)
        # self.zoomin_btn.setEnabled(True)
        # else:
        #     self.zoomout_btn.setDisabled(True)
        #     self.zoomin_btn.setEnabled(True)

    def normal_size(self):
        """ show page size """
        self.scale_factor = 1
        self.scale_image(0.38)
        self.normal_size_btn.setDisabled(True)

    def scale_image(self, factor):
        self.scale_factor *= factor
        # resize image
        self.image_label.resize(self.scale_factor)

        self.adjust_scrollbar(self.horizontalScrollBar(), factor)
        self.adjust_scrollbar(self.verticalScrollBar(), factor)

    def adjust_scrollbar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                               + ((factor - 1) * scrollBar.pageStep() / 2)))
