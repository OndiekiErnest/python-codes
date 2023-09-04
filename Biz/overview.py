from customs.utils import Line
from customs.buttons import Button
from customs.edits import MaskedEdit
from customs.views import ListView
from PyQt6.QtWidgets import (
    QGroupBox, QHBoxLayout,
    QFormLayout, QLabel,
    QWidget, QVBoxLayout,
)


class Section(QWidget):
    """ section to display overview details, like, sales """

    __slots__ = ("main_layout", "section_name", "section_label",
                 )

    def __init__(self, sect_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_layout = QFormLayout(self)

        self.section_name = Button(sect_name)
        self.section_label = MaskedEdit("23 pcs")
        self.section_label.setReadOnly(True)
        self.main_layout.addRow(self.section_name, self.section_label)


class Sales(Section):
    """ sales section """

    __slots__ = ("result_name", "result_label",
                 "add_new")

    def __init__(self, sect_name, result, bottom_name, *args, **kwargs):
        super().__init__(sect_name, *args, **kwargs)

        # result of, example, sales
        self.result_name = Button(result)
        self.result_label = MaskedEdit("Kshs 15,000")
        self.result_label.setReadOnly(True)
        self.main_layout.addRow(self.result_name, self.result_label)
        # add new button
        self.add_new = Button(bottom_name)
        self.main_layout.addRow(self.add_new)


class Stock(Section):
    """ stock section """

    __slots__ = ("result_name", "result_label", "add_new")

    def __init__(self, sect_name, result, bottom_name, *args, **kwargs):
        super().__init__(sect_name, *args, **kwargs)

        # result of, example, sales
        self.result_name = Button(result)
        self.result_label = MaskedEdit("Kshs 15,000")
        self.result_label.setReadOnly(True)
        self.main_layout.addRow(self.result_name, self.result_label)
        # add new button
        self.add_new = Button(bottom_name)
        self.main_layout.addRow(self.add_new)


class OutOfStock(QWidget):
    """ categories section """

    __slots__ = ("main_layout", "list_view")

    def __init__(self, *args, title="Out of Stock", **kwargs):
        super().__init__(*args, **kwargs)

        self.main_layout = QVBoxLayout(self)

        outOfStock_group = QGroupBox(title)
        outOfStock_group.setObjectName("innerGroup")
        self.main_layout.addWidget(outOfStock_group)  # add groupbox to main layout
        # create layout for the groupbox
        group_layout = QVBoxLayout(outOfStock_group)
        # list view for out of stock items
        self.list_view = ListView()
        group_layout.addWidget(self.list_view)


class Requests(OutOfStock):
    """ requests section """

    __slots__ = ("add_new", )

    def __init__(self, bottom_name, *args, title="Out of Stock", **kwargs):
        super().__init__(*args, title=title, **kwargs)

        # add new button
        self.add_new = Button(bottom_name)
        self.main_layout.addWidget(self.add_new)


class OverviewWindow(QGroupBox):
    """ window to display Overview items """

    __slots__ = ("main_layout", )

    def __init__(self, db_conn, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("overviewWindow")

        self.db_connection = db_conn

        self.main_layout = QHBoxLayout(self)

        self.create_widgets()

    def create_widgets(self):
        """ create widgets for Overview window """
        # sales section
        self.sales = Sales("Sales", "Profit", "Add New Sale")
        self.main_layout.addWidget(self.sales)
        self.main_layout.addWidget(Line(h=0))

        # total stock section
        self.stock = Stock("Stock", "Cost", "Add New Stock")
        self.main_layout.addWidget(self.stock)
        self.main_layout.addWidget(Line(h=0))
        # outofstock section
        self.outofstock = OutOfStock()
        self.main_layout.addWidget(self.outofstock)
        self.main_layout.addWidget(Line(h=0))
        # requests section
        self.requests = Requests("Add New Request", title="Requests")
        self.main_layout.addWidget(self.requests)

        # self.main_layout.addStretch()

    def add_request(self, brand_name: str):
        """ increment requests with brand_name """
        self.requests.list_view.addItem(brand_name)

    def add_outofstock(self, brand_name: str):
        """ update out of stock items """
        self.outofstock.list_view.addItem(brand_name)

    def add_stock(self, total: int):
        """ add total stock count """
        self.stock.section_label.setText(f"{total:,} Pcs")

    def add_sales(self, total: int):
        """ add total sales count """
        self.sales.section_label.setText(f"{total:,} Pcs")
