from categorygui import CategoryWindow
from creditgui import CreditWindow
from requestsgui import RequestsWindow
from salesgui import SalesWindow
from overview import OverviewWindow
from customs.buttons import Button
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QToolButton,
)
from PyQt6.QtSql import QSqlDatabase
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize


class HomeWindow(QWidget):
    """ window for holding Home window widgets """

    __slots__ = ("main_layout", "windows_layout",
                 "leftside_layout", "rightside_layout",
                 "db_connection",
                 )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("homeWindow")

        # main layout to hold all other widgets and layouts
        self.main_layout = QVBoxLayout(self)

        self.windows_layout = QHBoxLayout()

        self.leftside_layout = QVBoxLayout()
        self.rightside_layout = QVBoxLayout()
        # open application-wise db
        self.db_connection = QSqlDatabase("QSQLITE")
        self.db_connection.setDatabaseName("allowed.sqlite")
        self.db_connection.open()

        self.create_widgets()
        self.create_windows()

    def create_widgets(self):
        """ create Home window widgets """
        pass

    def create_windows(self):
        """ create different windows """
        # overview area of QGroupBox
        self.overview_win = OverviewWindow(self.db_connection, "Overview")
        self.overview_win.add_stock(7783)
        self.overview_win.add_outofstock("Predator Energy Drink")
        self.overview_win.add_request("Tusker Malt")
        # add overview QGroupBox first
        self.main_layout.addWidget(self.overview_win, stretch=1)
        # add windows layout
        self.main_layout.addLayout(self.windows_layout, stretch=2)

        # left side layout, then windows, then right side layout
        self.windows_layout.addLayout(self.leftside_layout)

        # categories area of type QGroupBox
        self.categories_win = CategoryWindow(self.db_connection, "Categories")
        self.windows_layout.addWidget(self.categories_win)

        self.windows_layout.addLayout(self.rightside_layout)

    def update_requests(self, brand_name: str):
        """ update stock to relevant windows """
        self.overview_win.add_request(brand_name)

    def update_outofstock(self, brand_name: str):
        """ update total outofstock to relevant windows """
        self.overview_win.add_outofstock(brand_name)

    def update_stock(self, total: int):
        """ update stock to relevant windows """
        self.overview_win.add_stock(total)

    def update_sales(self, total: int):
        """ update stock to relevant windows """
        self.overview_win.add_sales(total)

    def add_new_sale(self):
        """
        create new sales table if not found
        add new sale item
        """

    def add_new_stock(self):
        """
        create new stocks table if not found
        add new stock item
        """
