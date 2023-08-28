__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import pandas as pd
from PyQt5.QtCore import QSortFilterProxyModel, Qt, QAbstractTableModel, pyqtSignal
import common
# from asfaWatcher import Watcher

models_logger = common.logging.getLogger(__name__)
models_logger.debug(f"Initializing {__name__}")


class SortFilterModel(QSortFilterProxyModel):
    """
    model for implementing search/sort feature
    """

    # def lessThan(self, left, right):
    #     """
    #     over-ride the parent class lessThan method to sort int
    #     THIS METHOD SORTS SLOWLY COMPARED TO THE BELOW sort
    #     """

    #     if not (left.isValid() and right.isValid()):
    #         return False
    #     col = left.column()

    #     data_left = left.data()
    #     data_right = right.data()
    #     if col == 3:
    #         data_left = common.to_bytes(data_left)
    #         data_right = common.to_bytes(data_right)
    #     return data_left < data_right

    def sort(self, column, order):
        """ sort based on column and order """
        self.layoutAboutToBeChanged.emit()
        # use the source model sort function
        self.sourceModel().sort(column, order)

        self.layoutChanged.emit()

    def removeRows(self, selected: set):
        """ remove list of rows """
        # remove all rows from model before changing layout
        if selected:
            self.layoutAboutToBeChanged.emit()
            for name in selected:
                self.sourceModel().delete_name(name)
            self.layoutChanged.emit()


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
            # only icons to be displayed
            if index.column() == 1:
                return ""
            elif index.column() == 3:
                return common.convert_bytes(value)
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
        models_logger.debug(f"Sort Share files, 'a' order: {order}, column: {col}")

        # sorting
        self.dataSource.sort_values(by=column, ascending=order, inplace=True)

        self.layoutChanged.emit()

    def _change_icon(self, name, code):
        """ change status code of `name` hence its icon """

        name = common._basename(name)
        row_filter = self.file_filter(name)
        # change the cell value to `code`
        try:
            index = self.dataSource.loc[row_filter].index.to_list()[0]
            self.dataSource.at[row_filter, "Status"] = code
            # data changed on only a cell
            self.dataChanged.emit(self.index(index, 1), self.index(index, 1))
            models_logger.debug(f"Changed icon code for '{name}'")
        except Exception:
            pass

    def file_filter(self, filename):
        """
        filter based on filename
        """

        return self.dataSource["Name"] == filename

    def removeRows(self, selected: set):
        """ remove list of rows """
        # remove all rows from model before changing layout
        if selected:
            self.layoutAboutToBeChanged.emit()
            filt = self.file_filter
            for name in selected:
                self.dataSource.drop(index=self.dataSource[filt(name)].index, inplace=True, errors="ignore")
                models_logger.debug(f"Share files model: dropped '{name}'")
            self.layoutChanged.emit()

    def setup_model(self, generator):
        """ create storage for our data """

        self.beginResetModel()
        self.dataSource = pd.DataFrame([row for row in generator if row], columns=self.header)
        self.dataSource = self.dataSource.astype({"Status": "int8", "Type": "category", "Size": "category"})
        models_logger.debug(f"Share files model: {type(self.dataSource)}")
        self.dataSource.info(memory_usage="deep")
        self.sort(2, Qt.DescendingOrder)
        self.endResetModel()


class DiskFilesModel(QAbstractTableModel):
    """
    custom disk files model
    using a python pandas for storage
    it's notably fast in sorting,
    slower than python list in starting
    """

    def __init__(self, generators, header: tuple, *args):
        super().__init__(*args)
        self.header = header
        self.setup_model(generators)
        # self.files_watcher = Watcher(disk_path)
        # assign signals to slots
        # self.files_watcher.events.created.connect(self.append_row)
        # self.files_watcher.events.moved.connect(self.rename_row)
        # self.files_watcher.events.deleted.connect(self.delete_name)
        # start disk observer
        # self.files_watcher.observer_start()

    def rowCount(self, parent):
        rows = self.dataSource.shape[0]
        return rows

    def columnCount(self, parent):
        return self.dataSource.shape[1]

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return

        value = self.dataSource.iloc[index.row(), index.column()]

        if role == Qt.DisplayRole:
            # add 'File' to extension
            if index.column() == 2:
                return f"{value} File"
            # convert size to human readable
            elif index.column() == 3:
                return common.convert_bytes(value)
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

        column = self.dataSource.columns[col]
        order = (order == Qt.AscendingOrder)
        models_logger.debug(f"Sort Disk files, 'a' order: {order}, column: {col}")

        # sorting
        self.dataSource.sort_values(by=column, ascending=order, inplace=True)

    def file_filter(self, filename):
        """
        filter based on filename
        """

        name, dir_name = common._basename(filename), common.os.path.dirname(filename)
        return (self.dataSource["Name"] == name) & (self.dataSource["File Path"] == dir_name)

    def delete_name(self, name):
        """ delete filtered row """

        filt = self.file_filter(name)
        self.dataSource.drop(index=self.dataSource[filt].index, inplace=True, errors="ignore")
        models_logger.debug(f"Removed: '{name}'")

    # def append_row(self, name):
    #     """
    #     add new file to rows
    #     HONESTLY, this is what disqualifies pandas
    #     """

    #     print("APPENDING >>>", name)
    #     self.layoutAboutToBeChanged.emit()
    #     details = common.get_file_details(name)
    #     self.dataSource = self.dataSource.append(
    #         {"Name": details[0], "File Path": details[1], "Type": details[2], "Size": details[3]},
    #         ignore_index=True)
    #     self.layoutChanged.emit()

    # def rename_row(self, old, new):
    #     """ rename file """

    #     print("RENAMING >>>", old, new)
    #     self.layoutAboutToBeChanged.emit()
    #     filt = self.file_filter(old)
    #     details = common.get_file_details(new)
    #     self.dataSource.at[filt, ["Name", "File Path"]] = details[:2]
    #     self.layoutChanged.emit()

    def setup_model(self, generators):
        """ create storage for our data """

        self.beginResetModel()
        self.dataSource = pd.DataFrame([row for generator in generators for row in generator if row],
                                       columns=self.header)
        self.dataSource = self.dataSource.astype({"File Path": "category", "Type": "category"})
        models_logger.debug(f"Disk files model: {type(self.dataSource)}")
        self.dataSource.info(memory_usage="deep")
        self.endResetModel()
