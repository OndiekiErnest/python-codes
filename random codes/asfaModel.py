from PyQt5.QtCore import QSortFilterProxyModel
from datetime import datetime


def date_key(value: str) -> datetime:
    return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")


def size_key(value: str) -> float:
    size, unit = value.split(" ")
    size = float(size)
    if unit == "GB":
        return size * 1073741824
    elif unit == "MB":
        return size * 1048576
    elif unit == "KB":
        return size * 1024
    else:
        return size


class SortFilterModel(QSortFilterProxyModel):
    """
        model for implementing search/sort feature
    """

    def lessThan(self, left, right):
        """
            over-ride the subclass lessThan to sort datetime and int
        """

        col = left.column()

        data_left = left.data()
        data_right = right.data()
        if col == 1:
            data_left = date_key(data_left)
            data_right = date_key(data_right)
        elif col == 3:
            data_left = size_key(data_left)
            data_right = size_key(data_right)
        return data_left < data_right
