__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import pandas as pd
from PyQt5.QtCore import QSortFilterProxyModel, Qt, QAbstractTableModel, pyqtSignal
import common
import os
import operator
from asfaWatcher import Watcher


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
            data_left = common.to_bytes(data_left)
            data_right = common.to_bytes(data_right)
        return data_left < data_right


class ShareFilesModel(QAbstractTableModel):
    """
    custom share files model
    using a python pandas for storage
    it's notably fast in sorting,
    slower than python list in starting
    """

    feedback = pyqtSignal(str)

    def __init__(self, generator, header: tuple, icons: dict, *args):
        super().__init__(*args)
        self.header = header
        self.icons = icons
        self.setup_model(generator)

    def rowCount(self, parent):
        if isinstance(self.dataSource, pd.DataFrame):
            rows = self.dataSource.shape[0]
        elif isinstance(self.dataSource, list):
            rows = len(self.dataSource)
        self.feedback.emit(f"{rows:,} items")
        return rows

    def columnCount(self, parent):
        if isinstance(self.dataSource, pd.DataFrame):
            columns = self.dataSource.shape[1]
        elif isinstance(self.dataSource, list):
            columns = len(self.dataSource[0])
        if not columns:
            self.feedback.emit("Empty folder")
        return columns

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return

        if isinstance(self.dataSource, pd.DataFrame):
            value = self.dataSource.iloc[index.row(), index.column()]
        elif isinstance(self.dataSource, list):
            value = self.dataSource[index.row()][index.column()]

        if role == Qt.DisplayRole:
            if index.column() == 3:
                return common.convert_bytes(value)
            # only icons to be displayed
            elif index.column() == 1:
                return ""
            return value

        if role == Qt.UserRole:
            # get the whole row
            if isinstance(self.dataSource, pd.DataFrame):
                row = tuple(self.dataSource.iloc[index.row()])
            elif isinstance(self.dataSource, list):
                row = self.dataSource[index.row()]
            return row

        if role == Qt.ToolTipRole:
            if index.column() == 0:
                return value

        if role == Qt.DecorationRole:
            # decorate only the second column
            if index.column() == 1:
                return self.icons.get(value, self.icons[0])

        if role == Qt.TextAlignmentRole:
            if index.column() in (2, 3):
                return Qt.AlignCenter

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if isinstance(self.dataSource, pd.DataFrame):
                header = str(self.dataSource.columns[col])
            elif isinstance(self.dataSource, list):
                header = self.header[col]
            return header
        return

    def sort(self, col, order):
        """ sort table by given column number col """

        self.layoutAboutToBeChanged.emit()

        order = (order == Qt.AscendingOrder)
        if isinstance(self.dataSource, pd.DataFrame):
            # old_index_list = self.persistentIndexList()
            # old_ids = self.dataSource.index.copy()
            column = self.dataSource.columns[col]
            # sorting
            self.dataSource.sort_values(by=column, ascending=order, inplace=True)

            # new_ids = self.dataSource.index
            # new_index_list = []
            # for index in old_index_list:
            #     indx = old_ids[index.row()]
            #     new_row = new_ids.get_loc(indx)
            #     new_index_list.append(self.index(new_row, index.column(), index.parent()))
            # self.changePersistentIndexList(old_index_list, new_index_list)
        elif isinstance(self.dataSource, list):
            self.dataSource.sort(key=operator.itemgetter(col), reverse=order)
        self.layoutChanged.emit()

    def _change_icon(self, name, code):
        """ change status code of `name` hence its icon """

        self.layoutAboutToBeChanged.emit()
        name = common._basename(name)
        if isinstance(self.dataSource, pd.DataFrame):
            row_filter = self.dataSource["Name"] == name
            # change the cell value to `code`
            self.dataSource.loc[row_filter, "Status"] = code
        elif isinstance(self.dataSource, list):
            index, row = self.row_from_name(name)
            self.dataSource[index] = (row[0], code, row[2], row[3])
        self.layoutChanged.emit()

    def index_from_name(self, name):
        index = 0
        for row in self.dataSource:
            if row[0] == name:
                return index, row
            index += 1

    def setup_model(self, generator):
        """ create storage for our data """

        self.beginResetModel()
        self.dataSource = [row for row in generator if row]
        if len(self.dataSource) > 3000:
            self.dataSource = pd.DataFrame(self.dataSource, columns=self.header)
            self.dataSource = self.dataSource.astype({"Status": "int8", "Type": "category", "Size": "category"})
            print(self.dataSource.info(memory_usage="deep"))
        self.endResetModel()


class DiskFilesModel(QAbstractTableModel):
    """
    custom disk files model
    using a python pandas for storage
    it's notably fast in sorting,
    slower than python list in starting
    """

    total_files = pyqtSignal(str)

    def __init__(self, generators, header: tuple, disk_path: str, *args):
        super().__init__(*args)
        self.header = header
        self.path_to_watch = disk_path
        self.setup_model(generators)
        self.files_watcher = Watcher(disk_path)
        # assign signals to slots
        self.files_watcher.events.created.connect(self.append_row)
        self.files_watcher.events.moved.connect(self.rename_row)
        self.files_watcher.events.deleted.connect(self.delete_name)
        # start disk observer
        self.files_watcher.observer_start()

    def rowCount(self, parent):
        rows = self.dataSource.shape[0]
        self.total_files.emit(f"{rows:,}")
        return rows

    def columnCount(self, parent):
        return self.dataSource.shape[1]

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return

        value = self.dataSource.iloc[index.row(), index.column()]
        if role == Qt.DisplayRole:

            return value

        if role == Qt.UserRole:
            # get the whole row
            return tuple(self.dataSource.iloc[index.row()])

        if role == Qt.ToolTipRole:
            if index.column() in (0, 1):
                return value

        if role == Qt.TextAlignmentRole:
            if index.column() in (2, 3):
                return Qt.AlignCenter

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self.dataSource.columns[col])
        return

    def sort(self, col, order):
        """ sort table by given column number col """

        self.layoutAboutToBeChanged.emit()
        # old_index_list = self.persistentIndexList()
        # old_ids = self.dataSource.index.copy()

        column = self.dataSource.columns[col]
        order = (order == Qt.AscendingOrder)

        # sorting
        self.dataSource.sort_values(by=column, ascending=order, inplace=True)

        # new_ids = self.dataSource.index
        # new_index_list = []
        # for index in old_index_list:
        #     indx = old_ids[index.row()]
        #     new_row = new_ids.get_loc(indx)
        #     new_index_list.append(self.index(new_row, index.column(), index.parent()))
        # self.changePersistentIndexList(old_index_list, new_index_list)
        self.layoutChanged.emit()

    def file_filter(self, filename):
        """
        to be called when our watcher reports a file delete event
        delete row of the deleted file
        """

        name, dir_name = common._basename(filename), os.path.dirname(filename)
        return (self.dataSource["Name"] == name) & (self.dataSource["File Path"] == dir_name)

    def delete_name(self, name):
        """ delete filtered rows """

        print("DROPPING >>>", name)
        self.layoutAboutToBeChanged.emit()
        filt = self.file_filter(name)
        self.dataSource.drop(index=self.dataSource[filt].index, inplace=True)
        self.layoutChanged.emit()

    def append_row(self, name):
        """
        add new file to rows
        HONESTLY, this is what disqualifies pandas
        """

        print("APPENDING >>>", name)
        self.layoutAboutToBeChanged.emit()
        details = common.get_file_details(name)
        self.dataSource = self.dataSource.append(
            {"Name": details[0], "File Path": details[1], "Type": details[2], "Size": details[3]},
            ignore_index=True)
        self.layoutChanged.emit()

    def rename_row(self, old, new):
        """ rename file """

        print("RENAMING >>>", old, new)
        self.layoutAboutToBeChanged.emit()
        filt = self.file_filter(old)
        details = common.get_file_details(new)
        self.dataSource.at[filt, ["Name", "File Path"]] = details[:2]
        self.layoutChanged.emit()

    def setup_model(self, generators):
        """ create storage for our data """

        self.beginResetModel()
        self.dataSource = pd.DataFrame([row for generator in generators for row in generator if row],
                                       columns=self.header)
        self.dataSource = self.dataSource.astype({"File Path": "category", "Type": "category", "Size": "category"})
        print(self.dataSource.info(memory_usage="deep"))
        self.endResetModel()
