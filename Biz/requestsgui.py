from customs.views import TableView
from PyQt6.QtWidgets import (
    QWidget,
)


class RequestsWindow(QWidget):
    """ window to display requests items """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setObjectName("requestsWindow")
