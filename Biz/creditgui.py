from customs.views import TableView
from PyQt6.QtWidgets import (
    QWidget,
)


class CreditWindow(QWidget):
    """ window to display credit items """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("creditWindow")
