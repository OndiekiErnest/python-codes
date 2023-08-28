__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


from PyQt5.QtCore import QSortFilterProxyModel, Qt, QAbstractTableModel
import operator
from common import to_bytes, convert_bytes


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


class ShareFilesModel(QAbstractTableModel):
    """
    custom model with fetchMore
    using a python list for storage
    it's notably slow in sorting
    """

    def __init__(self, generator, header: tuple, icons: dict, *args):
        super().__init__(*args)
        self.setup_model(generator)
        self.header = header
        self.icons = icons

    def rowCount(self, parent):
        return len(self.dataList)

    def columnCount(self, parent):
        return len(self.dataList[0])

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return

        value = self.dataList[index.row()][index.column()]
        if role == Qt.DisplayRole:
            if index.column() == 3:
                return convert_bytes(value)
            # only icons to be displayed
            elif index.column() == 1:
                return ""
            return value

        if role == Qt.UserRole:
            return value

        if role == Qt.ToolTipRole:
            if index.column() == 0:
                return value

        if role == Qt.DecorationRole:
            # decorate only the second column
            if index.column() == 1:
                name, f_exists, file_type, size = self.dataList[index.row()]
                return self.icons.get(f_exists, 0)

        if role == Qt.TextAlignmentRole:
            if index.column() in (2, 3):
                return Qt.AlignCenter

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return

    def sort(self, col, order):
        """ sort table by given column number col """
        try:
            self.layoutAboutToBeChanged.emit()
            self.dataList.sort(key=operator.itemgetter(col))
            if order == Qt.DescendingOrder:
                self.dataList.reverse()
            self.layoutChanged.emit()
        # if dataList is empty
        except IndexError:
            pass

    def setup_model(self, generator):
        self.beginResetModel()
        self.dataList = [row for row in generator]
        self.endResetModel()
