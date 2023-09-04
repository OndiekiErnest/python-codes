from PyQt6.QtWidgets import (
    QMainWindow,
    QMenuBar,
)
from PyQt6.QtGui import (
    QAction,
)
import custom
import sys
import styles


class MainWindow(QMainWindow):
    """ main app window """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("mainwin")

        self.vid_win = custom.VidWindow()
        self.setCentralWidget(self.vid_win)
        # create menus
        self.create_menus()

    def create_actions(self):
        """ create actions for menus """
        # file actions
        self.open_files = QAction("Open F&ile(s)")
        self.open_folder = QAction("Open Fo&lder")
        self.open_stream = QAction("Open Strea&m")
        self.open_from_clipboard = QAction("Open from &Clipboard")
        self.open_recent = QAction("Open &Recent")
        self.save_playlist = QAction("&Save Playlist")
        # playback actions
        self.play_speed_actn = custom.PlaySpeedAction(self)
        self.skip_10s = QAction("Skip +10s")
        self.skip_back10s = QAction("Skip -10s")
        self.play_pause_actn = QAction("Pl&ay/Pause")
        self.play_next_actn = QAction("&Next")
        self.play_prev_actn = QAction("Pre&v")

    def create_menus(self):
        """ create menu bar and menus """
        # create actions
        self.create_actions()
        # create menu bar
        self.menu_bar = self.menuBar()

        # file menu
        self.file_menu = self.menu_bar.addMenu("&File")
        self.file_menu.addAction(self.open_files)
        self.file_menu.addAction(self.open_folder)
        self.file_menu.addAction(self.open_stream)
        self.file_menu.addAction(self.open_from_clipboard)
        self.file_menu.addAction(self.open_recent)
        self.file_menu.addAction(self.save_playlist)
        # playback menu
        self.playback_menu = self.menu_bar.addMenu("&Playback")
        self.playback_menu.addAction(self.play_speed_actn)
        self.playback_menu.addAction(self.skip_10s)
        self.playback_menu.addAction(self.skip_back10s)
        self.playback_menu.addAction(self.play_pause_actn)
        self.playback_menu.addAction(self.play_next_actn)
        self.playback_menu.addAction(self.play_prev_actn)

    def mouseDoubleClickEvent(self, event):
        """ override double-click """
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

        return super().mouseDoubleClickEvent(event)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyleSheet(styles.STYLE)

    win = MainWindow()
    win.showMaximized()

    sys.exit(app.exec())
