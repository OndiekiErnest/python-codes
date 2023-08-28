from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileSystemModel, QMainWindow, QTableView, QApplication
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel

# class FileModel(QFileSystemModel):

#     def __init__(self, *args, **kwargs):
#         super(FileModel, self).__init__(*args, **kwargs)

#     def headerData(self, section, orientation, role):

#         if role == Qt.TextAlignmentRole:
#             return Qt.AlignCenter
#         elif role == Qt.DecorationRole:
#             return None
#         else:
#             return QFileSystemModel.headerData(self, section, orientation, role)

class Main(QMainWindow):

    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)

        db = QSqlDatabase.addDatabase("QSQLITE", "file_connection")
        db.setDatabaseName("files.sqlite")
        db.open()
        self.table = QTableView()
        model = QSqlTableModel(db=db)
        self.table.setModel(model)
        model.setTable("disk")
        model.select()

        self.setCentralWidget(self.table)


if __name__ == '__main__':

    app = QApplication([])
    main = Main()
    main.show()

    app.exec_()
