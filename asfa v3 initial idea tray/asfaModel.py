from PyQt5.QtCore import QSortFilterProxyModel, Qt, QAbstractTableModel, QModelIndex


def to_bytes(value: str) -> float:
    """ convert a str (of the form, 'size unit') to float for sorting """
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
        over-ride the parent class lessThan method to sort int
        """

        if not (left.isValid() and right.isValid()):
            return False
        col = left.column()

        data_left = left.data()
        data_right = right.data()
        if col == 3:
            data_left = to_bytes(data_left)
            data_right = to_bytes(data_right)
        return data_left < data_right


class ShareFilesModel(QSortFilterProxyModel):
    """
    model for implementing search/sort feature
    """

    def lessThan(self, left, right):
        """
        over-ride the parent class lessThan method to sort int
        """

        if not (left.isValid() and right.isValid()):
            return False
        col = left.column()

        data_left = left.data()
        data_right = right.data()
        if col == 2:
            data_left = to_bytes(data_left)
            data_right = to_bytes(data_right)
        return data_left < data_right


class TableModel(QAbstractTableModel):
    """
    custom model with fetchMore
    using a python list for storage
    it's notably slow in sorting
    """

    def __init__(self, generators: list, header: tuple, *args):
        super().__init__(*args)
        self.setup_model(generators)
        self.header = header

    def rowCount(self, parent):
        return len(self.dataList)

    def columnCount(self, parent):
        return len(self.dataList[0])

    def data(self, index, role):
        if not index.isValid():
            return

        value = self.dataList[index.row()][index.column()]
        if role == Qt.DisplayRole:
            return value

        if role == Qt.ToolTipRole:
            if index.column() == 0 or index.column() == 1:
                return value

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return

    def canFetchMore(self, index):
        if index.isValid():
            return False
        return self.row_count < len(self.dataList)

    def fetchMore(self, index):
        if index.isValid():
            return
        remaining = len(self.dataList) - self.row_count
        to_fetch = min(100, remaining)
        # fetch more
        self.beginInsertRows(QModelIndex(), self.row_count, self.row_count + to_fetch)
        self.row_count += to_fetch
        # end fetching
        self.endInsertRows()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setup_model(self, generators: tuple):
        self.beginResetModel()
        self.dataList = [row for generator in generators for row in generator]
        self.row_count = 0
        self.endResetModel()
