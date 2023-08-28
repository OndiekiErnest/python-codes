# systemtray app using Qt
from PyQt5.QtWidgets import QApplication, QAction, QSystemTrayIcon, QMenu, QWidgetAction, QRadioButton, QHBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class TrayMenu(QMenu):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # declare icons
        self.video_icon = QIcon()
        self.doc_icon = QIcon()
        self.audio_icon = QIcon()
        self.image_icon = QIcon()

        # first row
        self.rbuttons_holder = QWidget(self)
        self.hlayout = QHBoxLayout(self)
        # self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.copy_rbutton = QRadioButton("Copy")
        self.copy_rbutton.clicked.connect(self.copy_selected)
        self.copy_rbutton.click()
        self.cut_rbutton = QRadioButton("Cut")
        self.cut_rbutton.clicked.connect(self.cut_selected)
        self.hlayout.addWidget(self.copy_rbutton, alignment=Qt.AlignRight)
        self.hlayout.addWidget(self.cut_rbutton, alignment=Qt.AlignRight)
        self.rbuttons_holder.setLayout(self.hlayout)
        self.first_action = QWidgetAction(self)
        self.first_action.setDefaultWidget(self.rbuttons_holder)
        self.addAction(self.first_action)

    def create_videos_action(self):
        # videos present
        self.videos_action = QAction(f"{self.selected} all Videos")
        # self.videos_action.triggered.connect
        self.addAction(self.videos_action)

    def create_documents_action(self):
        # documents present
        self.doc_action = QAction(f"{self.selected} all Documents")
        self.addAction(self.doc_action)

    def create_audio_action(self):
        # audio present
        self.audio_action = QAction(f"{self.selected} all Audio")
        self.addAction(self.audio_action)

    def create_images_action(self):
        # images present
        self.images_action = QAction(f"{self.selected} all Images")
        self.addAction(self.images_action)

    def create_buttons(self):
        # quit and more buttons
        self.addSeparator()
        self.abuttons_holder = QWidget(self)
        hlayout = QHBoxLayout(self)
        self.quit = QPushButton("Quit")
        self.more = QPushButton("More...")
        hlayout.addWidget(self.quit)
        hlayout.addWidget(self.more)
        self.abuttons_holder.setLayout(hlayout)
        self.last_action = QWidgetAction(self)
        self.last_action.setDefaultWidget(self.abuttons_holder)
        self.addAction(self.last_action)

    def create_all(self):
        self.create_videos_action()
        self.create_documents_action()
        self.create_audio_action()
        self.create_images_action()
        self.create_buttons()

    def copy_selected(self):
        self.selected = "Copy"
        self.update_text()

    def cut_selected(self):
        self.selected = "Cut"
        self.update_text()

    def update_text(self):
        try:
            self.videos_action.setText(f"{self.selected} all Videos")
            self.doc_action.setText(f"{self.selected} all Documents")
            self.audio_action.setText(f"{self.selected} all Audio")
            self.images_action.setText(f"{self.selected} all Images")
        except AttributeError:
            pass


if __name__ == '__main__':

    app = QApplication([])
    app.setQuitOnLastWindowClosed(0)
    icon = QIcon("C:\\Users\\code\\Pictures\\add_121935.png")

    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(1)

    menu = TrayMenu()
    menu.create_all()
    menu.quit.clicked.connect(app.quit)

    tray.setContextMenu(menu)
    tray.setToolTip("asfa - Test")
    app.exec_()
