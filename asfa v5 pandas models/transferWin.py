from PyQt5.QtWidgets import (
    QFormLayout, QVBoxLayout, QWidget, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QCheckBox, QLineEdit, QApplication, QGroupBox, QRadioButton,
    QFileDialog,
)
from PyQt5.QtCore import Qt
import os


class FolderTransferWin(QWidget):
    """
    create a window to popup when a flash-disk is inserted
    """

    def __init__(self, tray, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("folder_popup")
        self.setFixedSize(600, 300)
        self.setWindowTitle("asfa - Quick Transfer")

        self.tray_obj = tray

        # define layouts
        self.form_layout = QFormLayout()
        self.left_v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.grid_layout = QGridLayout()
        # define groupboxes
        self.right_group = QGroupBox("Select file extensions to skip")
        self.right_group.setObjectName("extensionsGroup")
        self.bottom_left_group = QGroupBox("More options")
        self.bottom_left_group.setObjectName("optionsGroup")

        self.copy_flag = QRadioButton("Copy")
        self.copy_flag.setChecked(1)
        self.move_flag = QRadioButton("Cut")
        self.recurse = QCheckBox("Transfer source sub-folders")
        self.recurse.setChecked(1)
        self.remember_disk_option = QCheckBox("Remember these choices (for this disk only)")
        self.remember_disk_option.setToolTip("""Attempt similar file transfer automatically
the next time you insert this disk.""")
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.get_selections)

        # nest layouts and set the main one to the main window
        self.h_layout.addLayout(self.left_v_layout)
        self.h_layout.addWidget(self.right_group)
        self.right_group.setLayout(self.grid_layout)
        self.setLayout(self.h_layout)

        self.create_first_column()
        self.create_last_column()

    def create_first_column(self):
        left_title = QLabel("Choose folder to transfer:")
        self.transfer_from_folder_input = QLineEdit()
        self.transfer_from_folder_input.setPlaceholderText("Source folder")
        transfer_from_browser = QPushButton("From")
        transfer_from_browser.clicked.connect(self.update_from_input)
        self.transfer_to_folder_input = QLineEdit()
        self.transfer_to_folder_input.setPlaceholderText("Destination folder")
        transfer_to_browser = QPushButton("To")
        transfer_to_browser.clicked.connect(self.update_to_input)

        # dir chooser section
        self.form_layout.addRow(transfer_from_browser, self.transfer_from_folder_input)
        self.form_layout.addRow(transfer_to_browser, self.transfer_to_folder_input)

        # more settings group
        more_v_layout = QVBoxLayout()
        self.bottom_left_group.setLayout(more_v_layout)
        more_v_layout.addWidget(self.copy_flag)
        more_v_layout.addWidget(self.move_flag)
        more_v_layout.addWidget(self.recurse)
        more_v_layout.addWidget(self.remember_disk_option)

        self.left_v_layout.addWidget(left_title, alignment=Qt.AlignTop)
        self.left_v_layout.addLayout(self.form_layout, stretch=1)
        self.left_v_layout.addWidget(self.bottom_left_group)
        self.left_v_layout.addWidget(self.ok_button, alignment=Qt.AlignRight)

    def create_last_column(self):
        exts = [".MKV", ".MP4", ".MP3", ".3gp", ".png", ".pdf", ".txt", ".wav", ".rtf"]
        row, col = 0, 0
        data_len = len(exts)
        col_size = 5 if data_len > 25 else 2
        for r in range(data_len):
            try:
                self.grid_layout.addWidget(QCheckBox(exts[r]), row, col)
                col += 1
                if col == col_size:
                    row, col = row + 1, 0
            except IndexError:
                break

    def update_from_input(self):
        folder_str = self.get_dir()
        self.transfer_from_folder_input.setText(folder_str)

    def update_to_input(self):
        folder_str = self.get_dir()
        self.transfer_to_folder_input.setText(folder_str)

    def get_dir(self):
        """ open dir chooser """
        folder = os.path.normpath(QFileDialog.getExistingDirectory(
            self, caption="asfa - Choose a folder to share",
            directory=os.path.expanduser("~\\Downloads")
        ))
        return folder

    def get_selections(self):
        source_folder = self.transfer_from_folder_input.text()
        dest_folder = self.transfer_to_folder_input.text()
        copy = self.copy_flag.isChecked()
        cut = self.move_flag.isChecked()
        recurse = self.recurse.isChecked()
        save_selection = self.remember_disk_option.isChecked()
        item_at = self.grid_layout.itemAt
        total_widgets = self.grid_layout.count() - 1
        ignore_patterns = [item_at(i).widget().text() for i in range(total_widgets) if item_at(i).widget().isChecked()]
        return source_folder, dest_folder, copy, cut, recurse, save_selection, ignore_patterns

    # def closeEvent(self, e):
    #     """ on window close """
    #     self.tray_obj.show()
    #     self.hide()
    #     e.ignore()


if __name__ == '__main__':
    app = QApplication([])
    win = FolderTransferWin(None)
    win.show()

    app.exec()
