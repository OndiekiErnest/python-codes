from customs.views import TableView
from PyQt6.QtWidgets import (
    QWidget,
)


class SalesWindow(QWidget):
    """ window to display sales items """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("salesWindow")
