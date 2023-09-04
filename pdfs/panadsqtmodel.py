__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


import pandas as pd
from PyQt6.QtCore import (
    QSortFilterProxyModel,
    QModelIndex,
    QAbstractTableModel,
    Qt, QThread,
    pyqtSignal, pyqtSlot,
)

# orientation
HORIENT = Qt.Orientation.Horizontal
VORIENT = Qt.Orientation.Vertical
# roles
DISPLAYROLE = Qt.ItemDataRole.DisplayRole
DECORROLE = Qt.ItemDataRole.DecorationRole
TALIGNROLE = Qt.ItemDataRole.TextAlignmentRole
TIPROLE = Qt.ItemDataRole.ToolTipRole
USERROLE = Qt.ItemDataRole.UserRole


class DataThread(QThread):
    """ populate data thread """
    __slots__ = ("data", "headers")

    result = pyqtSignal(object)

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTerminationEnabled(True)

        self.data = data

    @pyqtSlot()
    def run(self):

        rows = [row for generator in self.data for row in generator if row]
        self.result.emit(rows)

    def __del__(self):
        self.quit()
        self.wait()
        del self


class BaseModel(QAbstractTableModel):
    """ base model to inherit from """

    BATCH_COUNT = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dataSource = pd.DataFrame()

        self.rows_loaded = self.BATCH_COUNT

    def rowCount(self, parent):
        # len(df.index) is faster than dataSource.shape
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
        if orientation == HORIENT and role == DISPLAYROLE:
            return str(self.dataSource.columns[section])

    def canFetchMore(self, index):
        """ if there is more data to be fetched return True """
        if len(self.dataSource.index) > self.rows_loaded:
            return True
        else:
            return False

    def fetchMore(self, index):
        """ get the next batch of data """
        remaining = len(self.dataSource.index) - self.rows_loaded
        to_fetch = min(remaining, self.BATCH_COUNT)
        # beginInsertRows(parent, start, end)
        # for a table (which is not hierarchical like Treeview),
        # parent should be an invalid QModelIndex, meaning inserted items are at the root
        self.beginInsertRows(QModelIndex(), self.rows_loaded,
                             self.rows_loaded + to_fetch)
        self.rows_loaded += to_fetch
        self.endInsertRows()

    def _fallback_func(self, index):
        """ func to be called on undefined roles """
        return

    def _alignment_role(self, index):
        """ align text, return Qt.AlignmentFlags """

    def setup(self, df):
        self.beginResetModel()
        self.dataSource = df
        self.endResetModel()


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


class PandasModel(BaseModel):
    """
    custom share files model
    using a python pandas for storage
    it's notably fast in sorting,
    slower than python list in starting
    """

    def __init__(self, header: tuple, icons: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.header = header
        self.icons = icons
        self.data_thread = DataThread(None)
        self.data_thread.result.connect(self._update_model)
        self.data_routes = {
            DISPLAYROLE: self._display_role,
            USERROLE: self._user_role,
            TIPROLE: self._tooltip_role,
            DECORROLE: self._decoration_role,
            TALIGNROLE: self._alignment_role,
        }

    def data(self, index: QModelIndex, role=DISPLAYROLE):
        if not index.isValid():
            return

        func = self.data_routes.get(role, self._fallback_func)
        return func(index)

    def _decoration_role(self, index):
        """ return QIcon for a column """
        return

    def _tooltip_role(self, index):
        # get the tool tip for the 1st column
        if index.column() == 0:
            return self.dataSource.iloc[index.row(), index.column()]

    def _user_role(self, index):
        # get the whole row as a tuple
        return tuple(self.dataSource.iloc[index.row()])

    def _display_role(self, index):
        """ called for display role """
        value = self.dataSource.iloc[index.row(), index.column()]
        return value  # return actual value

    def sort(self, col, order):
        """ sort table by given column number col """

        try:
            column = self.dataSource.columns[col]
            order = (order == Qt.SortOrder.AscendingOrder)
            self.layoutAboutToBeChanged.emit()
            # sorting
            self.dataSource.sort_values(
                by=column, ascending=order, inplace=True)
            # done
            self.layoutChanged.emit()
        except IndexError:
            pass

    def file_filter(self, name):
        """ filter based on name """

        return self.dataSource["Name"] == name

    def removeRows(self, selected: set):
        """ remove list of rows """
        # remove all rows from model before changing layout
        if selected:
            self.layoutAboutToBeChanged.emit()
            filt = self.file_filter
            for name in selected:
                self.dataSource.drop(
                    index=self.dataSource[filt(name)].index,
                    inplace=True,
                    errors="ignore"
                )
            self.layoutChanged.emit()

    def delete_name(self, name):
        """ delete filtered row """

        filt = self.file_filter(name)
        self.dataSource.drop(
            index=self.dataSource[filt].index,
            inplace=True,
            errors="ignore"
        )

    def setup_model(self, generator):
        """ create storage for our data """
        # if a thread is running, disconnect it from _update_model
        self.data_thread.result.disconnect()
        self.data_thread = DataThread((generator, ))
        self.data_thread.result.connect(self._update_model)
        self.data_thread.start()

    def _update_model(self, dataList):
        dataSource = pd.DataFrame(dataList, columns=self.header)
        self.setup(dataSource)
