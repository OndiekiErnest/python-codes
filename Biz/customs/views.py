from PyQt6.QtWidgets import (
    QTableView, QHeaderView,
    QListWidget,
)


class TableView(QTableView):
    """ custom QTableView widget for displaying tabular data """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setShowGrid(False)
        self.setSelectionBehavior(self.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


class ListView(QListWidget):
    """ custom list view for listing items """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
