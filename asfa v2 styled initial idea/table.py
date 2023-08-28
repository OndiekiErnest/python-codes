import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QTableView, QHeaderView, QVBoxLayout, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from asfaModel import SortFilterModel
import os
import time


def convert_bytes(num: int):
    if num >= 1073741824:
        return f"{round(num / 1073741824, 2)} GB"
    elif num >= 1048576:
        return f"{round(num / 1048576, 2)} MB"
    elif num >= 1024:
        return f"{round(num / 1024, 2)} KB"
    else:
        return f"{num} Bytes"


def get_files(folder: str):
    """
        return the file and its stats
    """

    for entry in os.scandir(folder):
        if entry.is_file():
            _, ext = os.path.splitext(entry.name)
            ext = ext.strip(".").upper() + " File"
            stats = entry.stat()
            datec = time.ctime(stats.st_ctime)
            size = convert_bytes(stats.st_size)
            yield entry.name, datec, ext, size


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 500)
        mainLayout = QVBoxLayout()

        # companies = ('Apple', 'Facebook', 'Google', 'Amazon',
        #              'Walmart', 'Dropbox', 'Starbucks', 'eBay', 'Canon')
        files = get_files("C:\\Users\\code\\Music\\Playlists")
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(
            ["Names", "Date created", "Type", "Size"])

        for row in files:
            items = (QStandardItem(row[0]),
                     QStandardItem(row[1]),
                     QStandardItem(row[2]),
                     QStandardItem(row[3])
                     )
            model.appendRow(items)

        filter_proxy_model = SortFilterModel(self)
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(0)

        search_field = QLineEdit()
        search_field.setStyleSheet('font-size: 35px; height: 60px;')
        search_field.textChanged.connect(filter_proxy_model.setFilterRegExp)
        mainLayout.addWidget(search_field)

        table = QTableView()
        # table
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # table.setStyleSheet('font-size: 35px;')
        # table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(0)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setModel(filter_proxy_model)
        table.setSortingEnabled(1)
        table.setShowGrid(0)
        table.setAlternatingRowColors(1)
        table.setEditTriggers(table.NoEditTriggers)
        mainLayout.addWidget(table)

        self.setLayout(mainLayout)


app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
