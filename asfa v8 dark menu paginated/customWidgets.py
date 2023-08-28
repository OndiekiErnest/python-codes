from common import logging, os, OS_SEP, pyqtSignal, MACHINE_IP
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QLineEdit, QFileDialog, QPushButton, QFrame,
    QTabBar, QStyle, QStylePainter, QStyleOptionTab,
    QTabWidget, QHBoxLayout, QAction,
)


cw_logger = logging.getLogger(__name__)

cw_logger.debug(f"Initializing {__name__}")


# ---------------------- CUSTOM LINE -------------------------------------------------------


class Line(QFrame):
    def __init__(self, h=1):
        super().__init__()
        if h:
            # defaults to horizontal line
            self.setFrameShape(QFrame.HLine)
        else:
            self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        # self.setStyleSheet("background: #999")
# ---------------------- END CUSTOM LINE -------------------------------------------------------


class PathEdit(QLineEdit):
    """
    custom QLineEdit for path display, set to readOnly
    """

    def __init__(self, chooser_title, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.caption = chooser_title
        self.last_known_dir = os.path.expanduser(f"~{OS_SEP}Documents")

        self.setReadOnly(True)
        self.textChanged.connect(self.validate)
        add_action = QAction(self)
        add_action.setObjectName("addPathAction")
        add_action.setIcon(QIcon(f"data{OS_SEP}add_folder.png"))
        add_action.setToolTip("Browse")
        add_action.triggered.connect(self.get_dir)
        self.addAction(add_action, QLineEdit.TrailingPosition)

    def get_dir(self):
        """ set abs folder str """
        folder = os.path.normpath(QFileDialog.getExistingDirectory(
            self, caption=f"{self.caption}",
            directory=self.last_known_dir,
        ))
        if folder and folder != ".":
            self.last_known_dir = folder
            self.setText(folder)

    def validate(self, text: str):
        """ set text if it's a valid path """
        f_text = text if os.path.exists(text) else ""
        self.setText(f_text)


class PasswordEdit(QLineEdit):
    """
    custom QLineEdit for password display, with show/hide
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set masked input
        self.setEchoMode(QLineEdit.Password)
        self.add_folder = QAction(self)
        self.add_folder.setObjectName("showPasswordAction")
        self.add_folder.setIcon(QIcon(f"data{OS_SEP}show.png"))
        # since it defaults to hide, show on first click
        self.add_folder.triggered.connect(self.show)
        self.addAction(self.add_folder, QLineEdit.TrailingPosition)

    def show(self):
        """ show password """
        self.add_folder.triggered.disconnect()
        self.add_folder.setIcon(QIcon(f"data{OS_SEP}hide.png"))
        self.setEchoMode(QLineEdit.Normal)
        # when clicked again, hide
        self.add_folder.triggered.connect(self.hide)

    def hide(self):
        """ hide password """
        self.add_folder.triggered.disconnect()
        self.add_folder.setIcon(QIcon(f"data{OS_SEP}show.png"))
        self.setEchoMode(QLineEdit.Password)
        # when clicked again, show
        self.add_folder.triggered.connect(self.show)


# ------------------------------------ CUSTOM TAB WIDGET ------------------------------------------
class TabBar(QTabBar):
    """
        create vertical tabs with horizontal texts
    """

    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            # s = opt.rect.size()
            s = QSize(200, 300)
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            # set the font
            font = painter.font()
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class TabWidget(QTabWidget):
    """
        create vertical tabs with horizontal icons and texts
    """

    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QTabWidget.West)
# --------------------------------------------- END OF CUSTOM TAB WIDGET ---------------------------------


# custom search input
class SearchInput(QLineEdit):
    """
    custom QLineEdit for search
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # introduce files searched model

        self.setObjectName("searchInput")
        self.close_action = QAction(self)
        self.close_action.setIcon(QIcon(f"data{OS_SEP}search.png"))
        self.addAction(self.close_action, QLineEdit.TrailingPosition)
        self.textChanged.connect(self.on_type)

    def close_search(self):
        """ clear search area and change icon """
        self.close_action.setIcon(QIcon(f"data{OS_SEP}search.png"))
        self.close_action.triggered.disconnect()
        self.clear()

    def on_type(self, txt):
        """ change icon, close on action triggered """
        if txt:
            self.close_action.setIcon(QIcon(f"data{OS_SEP}cancel.png"))
            self.close_action.triggered.connect(self.close_search)
        else:
            self.close_action.setIcon(QIcon(f"data{OS_SEP}search.png"))
