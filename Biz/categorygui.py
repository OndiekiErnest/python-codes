from customs.views import TableView
from customs.edits import SearchInput
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout,
    QTabWidget, QWidget,
)
from PyQt6.QtCore import (
    Qt,
)
from models.category import CategoryModel


class CategoryWindow(QGroupBox):
    """ window to display category items """

    __slots__ = ("main_layout", "main_tab", "categories_list", "current_table")

    def __init__(self, db_conn, *args, catgr_list=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("categoryWindow")
        # db connection
        self.db_connection = db_conn

        self.main_layout = QVBoxLayout(self)

        # create search widget
        self.search_input = SearchInput()
        self.search_input.setFixedWidth(400)

        self.main_layout.addWidget(self.search_input,
                                   alignment=Qt.AlignmentFlag.AlignRight)
        # tab widget to hold tabbed widgets
        self.main_tab = QTabWidget()
        self.main_tab.setDocumentMode(True)
        self.main_tab.currentChanged.connect(self.tab_changed)
        self.main_tab.setMovable(True)

        self.main_layout.addWidget(self.main_tab)

        if catgr_list is None:
            # list of categories available
            self.categories_list = [
                ("All", None), ("Vodka", None),
                ("Whisky", None), ("Spirit", None),
                ("Wine", None), ("Cream", None),
            ]
        else:
            self.categories_list = catgr_list

        # create widgets for this window
        self.create_widgets()

    def tab_changed(self, index: int):
        """
        map table view to widget
        use one table, change models on currentChanged
        """
        self.current_table = self.main_tab.currentWidget()
        search_str = self.main_tab.tabText(index)
        # create and query model using (search_str)
        # then assign it to current_table
        if search_str != "All":
            self.model = CategoryModel(search_str, self.db_connection)
            self.current_table.setModel(self.model)
            # self.current_table.hideColumn(self.model.fieldIndex("id"))
            # self.current_table.hideColumn(self.model.fieldIndex("categoryId"))

    def create_widgets(self):
        """ create widgets for CategoryWindow """
        for label, icon in self.categories_list:
            table = TableView()
            self.addToTab(label, table, icon)

    def addToTab(self, label: str, widget: QWidget, icon=None):
        """ extend tabs with `widget` """
        if icon is None:
            self.main_tab.addTab(widget, label)
        else:
            self.main_tab.addTab(widget, icon, label)

    def insertToTab(self, index: int, label: str, widget: QWidget, icon=None):
        """ insert widget at a position """
        if icon is None:
            self.main_tab.insertTab(index, widget, label)
        else:
            self.main_tab.insertTab(index, widget, icon, label)
