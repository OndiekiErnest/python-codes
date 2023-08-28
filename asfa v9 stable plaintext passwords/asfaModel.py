__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import pandas as pd
from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex, QAbstractTableModel, Qt
import common
# from asfaWatcher import Watcher

models_logger = common.logging.getLogger(__name__)
models_logger.debug(f"Initializing {__name__}")


class BaseModel(QAbstractTableModel):
    """ base model to inheriting from """

    BATCH_COUNT = 30

    def __init__(self, df, *args):
        super().__init__(*args)

        self.rows_loaded = self.BATCH_COUNT

        self.beginResetModel()
        self.dataSource = df
        self.endResetModel()

    def rowCount(self, parent):
        # len(df.index) is faster
        rows = len(self.dataSource.index)
        if rows <= self.rows_loaded:
            return rows
        else:
            return self.rows_loaded

    def columnCount(self, parent):
        # len() is faster
        columns = len(self.dataSource.columns)
        return columns

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return str(self.dataSource.columns[section])

    def canFetchMore(self, index):
        """ if there is more data to be fetched """
        if self.dataSource.shape[0] > self.rows_loaded:
            return True
        else:
            return False

    def fetchMore(self, index):
        """ get the next batch of data """
        remaining = self.dataSource.shape[0] - self.rows_loaded
        to_fetch = min(remaining, self.BATCH_COUNT)
        # beginInsertRows(parent, start, end)
        # for a table (which is not hierarchical), parent should be an invalid QModelIndex, meaning inserted items are at the root
        self.beginInsertRows(QModelIndex(), self.rows_loaded, self.rows_loaded + to_fetch)
        self.rows_loaded += to_fetch
        self.endInsertRows()


class SortFilterModel(QSortFilterProxyModel):
    """
    model for implementing search/sort feature
    """

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


class ShareFilesModel(BaseModel):
    """
    custom share files model
    using a python pandas for storage
    it's notably fast in sorting,
    slower than python list in starting
    """

    def __init__(self, generator, header: tuple, icons: dict, *args):

        self.header = header
        self.icons = icons
        super().__init__(self.setup_model(generator), *args)
        # sort column 2
        # self.sort(2, Qt.DescendingOrder)

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

    def setup_model(self, generator) -> pd.DataFrame:
        """ create storage for our data """

        dataSource = pd.DataFrame([row for row in generator if row], columns=self.header)
        dataSource = dataSource.astype({"Status": "int8", "Type": "category", "Size": "category"})
        models_logger.debug(f"Share files model: {type(dataSource)}")
        dataSource.info(memory_usage="deep")
        return dataSource


class DiskFilesModel(BaseModel):
    """
    custom disk files model
    using a python pandas for storage
    it's notably fast in sorting,
    slower than python list in starting
    """

    def __init__(self, generators, header: tuple, *args):
        self.header = header
        super().__init__(self.setup_model(generators), *args)
        # self.files_watcher = Watcher(disk_path)
        # assign signals to slots
        # self.files_watcher.events.created.connect(self.append_row)
        # self.files_watcher.events.moved.connect(self.rename_row)
        # self.files_watcher.events.deleted.connect(self.delete_name)
        # start disk observer
        # self.files_watcher.observer_start()

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

    def setup_model(self, generators) -> pd.DataFrame:
        """ create storage for our data """

        dataSource = pd.DataFrame([row for generator in generators for row in generator if row], columns=self.header)
        dataSource = dataSource.astype({"File Path": "category", "Type": "category"})
        models_logger.debug(f"Disk files model: {type(dataSource)}")
        dataSource.info(memory_usage="deep")
        return dataSource
