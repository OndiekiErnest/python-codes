import operator
from PyQt5.QtCore import Qt, QAbstractTableModel
from datetime import datetime


def names_key(value: list) -> str:
    value = value[0].text()
    return value


def date_key(value: list) -> datetime:
    value = value[1]
    return datetime.strptime(value, "%a %b %d %H:%M:%S %Y")


def type_key(value: list) -> str:
    value = value[2]
    return value


def size_key(value: list) -> float:
    value = value[3]
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


class TableModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """

    def __init__(self, parent, mylist: list, header: tuple, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def setDataList(self, mylist):
        self.mylist = mylist
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(
            self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        if (index.column() == 0):
            value = self.mylist[index.row()][index.column()].text()
        else:
            value = self.mylist[index.row()][index.column()]
        if role == Qt.EditRole:
            return value
        elif role == Qt.DisplayRole:
            return value
        elif role == Qt.CheckStateRole:
            if index.column() == 0:
                if self.mylist[index.row()][index.column()].isChecked():
                    return Qt.Checked
                else:
                    return Qt.Unchecked

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        routes = {0: names_key, 1: date_key,
                  2: operator.itemgetter(col), 3: size_key}
        self.layoutAboutToBeChanged.emit()
        self.mylist.sort(key=routes[col])
        if order == Qt.DescendingOrder:
            self.mylist.reverse()
        self.layoutChanged.emit()

    def flags(self, index):
        if not index.isValid():
            return None
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.CheckStateRole and index.column() == 0:
            if value == Qt.Checked:
                self.mylist[index.row()][index.column()].setChecked(1)
            else:
                self.mylist[index.row()][index.column()].setChecked(0)
        self.dataChanged.emit(index, index)
        return True
