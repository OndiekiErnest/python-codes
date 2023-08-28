import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QTableView, QHeaderView, QVBoxLayout, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import QtCore
import os
from asfaModel import SortFilterModel


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 600)
        mainLayout = QVBoxLayout()

        companies = os.listdir("C:\\Users\\code\\Music")
        model = QStandardItemModel(len(companies), 1)
        model.setHorizontalHeaderLabels(['Files'])

        for row, company in enumerate(companies):
            item = QStandardItem(company)
            model.setItem(row, 0, item)

        filter_proxy_model = SortFilterModel(self)
        filter_proxy_model.setSourceModel(model)
        filter_proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        filter_proxy_model.setFilterKeyColumn(0)

        search_field = QLineEdit()
        search_field.setStyleSheet('font-size: 35px; height: 60px;')
        search_field.textChanged.connect(filter_proxy_model.setFilterRegExp)
        mainLayout.addWidget(search_field)

        table = QTableView()
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setStyleSheet('font-size: 20px;')
        # table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setModel(filter_proxy_model)
        table.setSortingEnabled(1)
        mainLayout.addWidget(table)

        self.setLayout(mainLayout)


app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
