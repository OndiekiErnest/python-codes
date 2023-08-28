__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import pandas as pd
from PyQt5.QtCore import QObject, QSortFilterProxyModel, Qt, QAbstractTableModel, pyqtSignal, QRunnable, pyqtSlot, QThreadPool
import common
import os
import operator
from asfaWatcher import Watcher


class RunnableSignals(QObject):
    """ signals """
    finished = pyqtSignal()
    started = pyqtSignal()
    error = pyqtSignal()


class ManagerSignals(QObject):
    """ manager signals """
    finished = pyqtSignal()


class ModelRunnable(QRunnable):
    """
    run `func` in thread
    """
    __slots__ = ("func", "args", "kwargs", "signals")

    def __init__(self, func, *args, **kwargs):
        super(QRunnable, self).__init__()
        self.setAutoDelete(True)
        self.signals = RunnableSignals()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        try:
            self.signals.started.emit()
            self.func(*self.args, **self.kwargs)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit()
            print("[Error]", e)


class RunnablesManager():

    def __init__(self):
        self.runnable_pool = QThreadPool()
        self.runnable_pool.setMaxThreadCount(1)
        self.active_runnables = 0
        self.manager_signals = ManagerSignals()

    def add(self, runnable: ModelRunnable):
        """ enqueue a runnable """
        self.active_runnables += 1
        runnable.signals.finished.connect(self.on_finish)
        self.runnable_pool.start(runnable)

    def on_finish(self):
        self.active_runnables -= 1
        # if all done
        if not self.active_runnables:
            self.manager_signals.finished.emit()


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
        rows = self.dataSource.shape[0]
        self.feedback.emit(f"{rows:,} items")
        return rows

    def columnCount(self, parent):
        columns = self.dataSource.shape[1]
        return columns

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return

        value = self.dataSource.iloc[index.row(), index.column()]
        if role == Qt.DisplayRole:
            if index.column() == 3:
                return common.convert_bytes(value)
            # only icons to be displayed
            elif index.column() == 1:
                return ""
            return value

        if role == Qt.UserRole:
            # get the whole row
            return tuple(self.dataSource.iloc[index.row()])

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
            return str(self.dataSource.columns[col])
        return

    def sort(self, col, order):
        """ sort table by given column number col """

        self.layoutAboutToBeChanged.emit()

        column = self.dataSource.columns[col]
        order = (order == Qt.AscendingOrder)

        # sorting
        self.dataSource.sort_values(by=column, ascending=order, inplace=True)
        self.layoutChanged.emit()

    def _change_icon(self, name, code):
        """ change status code of `name` hence its icon """

        self.layoutAboutToBeChanged.emit()
        name = common._basename(name)
        row_filter = self.dataSource["Name"] == name
        # change the cell value to `code`
        self.dataSource.loc[row_filter, "Status"] = code
        self.layoutChanged.emit()

    def setup_model(self, generator):
        """ create storage for our data """

        self.beginResetModel()
        self.dataSource = pd.DataFrame([row for row in generator if row], columns=self.header)
        self.dataSource = self.dataSource.astype({"Status": "int8", "Type": "category", "Size": "category"})
        print(self.dataSource.info(memory_usage="deep"))
        self.endResetModel()


class DiskFilesModel(QAbstractTableModel):
    """
    custom disk files model
    using a python list for storage
    it's notably faster than pandas in starting, appending,
    slower than pandas in sorting
    """

    def __init__(self, generators, header: tuple, disk_path: str, *args):
        super().__init__(*args)
        self.header = header
        self.setup_model(generators)
        self.files_watcher = Watcher(disk_path)
        # assign signals to slots
        self.files_watcher.events.created.connect(self.append_row)
        self.files_watcher.events.moved.connect(self.rename_row)
        self.files_watcher.events.deleted.connect(self.delete_row)
        # start disk observer
        self.files_watcher.observer_start()

    def rowCount(self, parent):
        return len(self.dataSource)

    def columnCount(self, parent):
        return len(self.dataSource[0])

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return

        value = self.dataSource[index.row()][index.column()]
        if role == Qt.DisplayRole:

            return value

        if role == Qt.UserRole:
            # get the whole row
            return self.dataSource[index.row()]

        if role == Qt.ToolTipRole:
            if index.column() in (0, 1):
                return value

        if role == Qt.TextAlignmentRole:
            if index.column() in (2, 3):
                return Qt.AlignCenter

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return

    def sort(self, col, order):
        """ sort table by given column number col """

        self.layoutAboutToBeChanged.emit()
        order = (order == Qt.AscendingOrder)

        # sorting
        self.dataSource.sort(key=operator.itemgetter(col), reverse=order)
        self.layoutChanged.emit()

    def delete_row(self, name):
        """ delete filtered rows """

        # print("DROPPING >>>", name)
        self.layoutAboutToBeChanged.emit()
        index = self.index_row(name)
        if index:
            del self.dataSource[index]
        else:
            self.drop_folder(name)
        self.layoutChanged.emit()

    def append_row(self, name):
        """
        add new file to rows
        appending is what disqualifies pandas
        """

        # print("APPENDING >>>", name)
        self.layoutAboutToBeChanged.emit()
        details = common.get_file_details(name)
        self.dataSource.append(details)
        self.layoutChanged.emit()

    def rename_row(self, old, new):
        """ rename file """

        # print("RENAMING >>>", old, new)
        index = self.index_row(old)
        details = common.get_file_details(new)
        self.dataSource[index] = details
        self.dataChanged.emit(self.index(index, 0), self.index(index, 0))

    def index_row(self, filename):
        name, dir_name = common._basename(filename), os.path.dirname(filename)
        for index, row in enumerate(self.dataSource):
            if (row[0] == name) and (row[1] == dir_name):
                return index

    def drop_folder(self, folder):

        for index, row in enumerate(self.dataSource[::-1]):
            # File Path column
            if (row[1] == folder):
                # print("DROPPING >>>", row)
                self.dataSource.remove(row)

    def setup_model(self, generators):
        """ create storage for our data """

        self.beginResetModel()
        self.dataSource = [row for generator in generators for row in generator if row]
        self.endResetModel()
