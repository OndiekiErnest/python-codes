import sys

from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from customWidgets import (
    PathEdit, QLineEdit, QPushButton, SearchInput,
    Line, pyqtSignal, MACHINE_IP, PasswordEdit, logging,
)

from PyQt5.QtWidgets import (
    QApplication,
    QDataWidgetMapper,
    QFormLayout,
    QHBoxLayout,
    QTableView,
    QVBoxLayout,
    QWidget, QLabel,
    QSpinBox,
)


ss_logger = logging.getLogger(__name__)

ss_logger.debug(f"Initializing {__name__}")


db = QSqlDatabase("QSQLITE")
db.setDatabaseName("allowed.sqlite")
is_open = db.open()

if is_open:
    ss_logger.debug("DB Open")

    class ServerSettingsWindow(QWidget):
        """ Server settings manager """

        new_user_signal = pyqtSignal(str, str, str)
        delete_user_signal = pyqtSignal(str)

        def __init__(self):
            super().__init__()

            # start query and create table first, before creating self.model [recommended]
            self.query = QSqlQuery(db=db)

            if not ("Users" in db.tables()):
                done = self.create_table()
                ss_logger.debug(f"Done creating Table: {done}")

            # prepare layouts
            main_hlayout = QHBoxLayout()
            server_cred_form_layout = QFormLayout()
            left_side_layout = QVBoxLayout()
            left_side_layout.addLayout(server_cred_form_layout)
            right_side_layout = QVBoxLayout()
            shared_dir_layout = QHBoxLayout()
            form = QFormLayout()

            server_ip = QLineEdit()
            # drag/drop text
            server_ip.setDragEnabled(True)
            server_ip.setReadOnly(True)
            server_ip.setToolTip("Your peers will use this to connect to your server")
            server_ip.setText(MACHINE_IP)

            self.server_password = PasswordEdit()
            self.server_password.setToolTip("Set one password for all users (recommended)\nGive this to your peers")
            self.server_password.setPlaceholderText("Password for your server")
            self.search_input = SearchInput()
            self.search_input.setPlaceholderText("Search...")
            # table view
            self.table_view = QTableView()
            self.table_view.verticalHeader().setVisible(False)
            self.table_view.setSelectionBehavior(QTableView.SelectRows)

            # database model
            self.model = QSqlTableModel(db=db)
            # get the Users table
            self.model.setTable("Users")

            self.proxy_model = QSortFilterProxyModel()
            self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
            self.proxy_model.setSourceModel(self.model)
            # self.proxy_model.sort(1, Qt.AscendingOrder)
            # search all columns
            self.proxy_model.setFilterKeyColumn(-1)
            self.table_view.setModel(self.proxy_model)
            # select
            self.model.select()

            # add password edit at the top
            server_cred_form_layout.addRow("Server Access Password", self.server_password)
            server_cred_form_layout.addRow("Server IP", server_ip)
            # search input and table on left
            right_side_layout.addWidget(self.search_input)
            right_side_layout.addWidget(self.table_view)

            # add left and right layouts
            main_hlayout.addLayout(left_side_layout)
            main_hlayout.addWidget(Line(h=0))
            main_hlayout.addLayout(right_side_layout)

            self.name = QLineEdit()
            self.name.setPlaceholderText("Peer Username")
            self.id_label = QSpinBox()
            self.id_label.setRange(0, 2147483645)
            self.id_label.setDisabled(True)
            self.allowed_folder = PathEdit("Select folder the user will access")
            self.allowed_folder.setPlaceholderText("Access folder")
            # shared folder choose area
            shared_dir_layout.addWidget(self.allowed_folder)

            form.addRow(QLabel("User details"))
            form.addRow(Line())
            form.addRow("Index", self.id_label)
            form.addRow("Username", self.name)
            form.addRow("Access Folder", shared_dir_layout)

            # search when filter changes
            self.search_input.textChanged.connect(self.proxy_model.setFilterFixedString)

            self.mapper = QDataWidgetMapper()
            self.mapper.setModel(self.proxy_model)

            self.mapper.addMapping(self.id_label, 0)
            self.mapper.addMapping(self.name, 1)
            self.mapper.addMapping(self.server_password, 2)
            self.mapper.addMapping(self.allowed_folder, 3)

            # Change the mapper selection using the table.
            self.table_view.selectionModel().currentRowChanged.connect(self.mapper.setCurrentModelIndex)
            self.table_view.clicked.connect(self.enable_remove_btn)

            self.mapper.toFirst()

            # buttons
            btn_layout = QHBoxLayout()

            add_record = QPushButton("Add User")
            add_record.setToolTip("Add new unique user")
            add_record.clicked.connect(self.add_user)

            self.remove_record = QPushButton("Remove User")
            self.remove_record.setDisabled(True)
            self.remove_record.clicked.connect(self.delete_user)

            prev_rec = QPushButton("<")
            prev_rec.clicked.connect(self.mapper.toPrevious)

            next_rec = QPushButton(">")
            next_rec.clicked.connect(self.mapper.toNext)

            save_rec = QPushButton("Save Changes")
            save_rec.setToolTip("Save changes\nRestart for changes to reflect")
            save_rec.clicked.connect(self.mapper.submit)

            btn_layout.addWidget(prev_rec)
            btn_layout.addWidget(add_record)
            btn_layout.addWidget(self.remove_record)
            btn_layout.addWidget(save_rec)
            btn_layout.addWidget(next_rec)

            left_side_layout.addLayout(form)
            left_side_layout.addLayout(btn_layout)

            self.setLayout(main_hlayout)

        def create_table(self):
            """ create sqlite table if none exists """
            ss_logger.debug("Creating Table")
            isTableCreated = self.query.exec(
                """
                CREATE TABLE Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(16) NOT NULL,
                shared_dir VARCHAR(256) NOT NULL
                )
                """)
            return isTableCreated

        def add_user(self):
            """ insert new user to db """
            # TODO: hash password before saving

            username, password = self.name.text(), self.server_password.text()
            shared_dir = self.allowed_folder.text()

            # creating a query using .prepare() for later execution
            self.query.prepare(
                """
                INSERT INTO Users (
                    username,
                    password,
                    shared_dir
                    )
                    VALUES (?, ?, ?)
                """
            )

            self.clear_text()
            if all((username, password, shared_dir)):
                ss_logger.debug("Adding new user to DB")
                self.query.addBindValue(username)
                self.query.addBindValue(password)
                self.query.addBindValue(shared_dir)
                isSuccess = self.query.exec()
                if not isSuccess:
                    ss_logger.debug(f"DB error {self.query.lastError().driverText()}")

                # emit for the server to pick up
                self.new_user_signal.emit(username, password, shared_dir)
                # make the changes reflect
                self.model.select()

        def delete_user(self):
            """ remove selected rows """
            indexes = self.table_view.selectionModel().selectedRows()
            for index in indexes:
                row = index.row()
                done = self.model.deleteRowFromTable(row)
                user = self.get_username(row)
                ss_logger.debug(f"Removing {user} {done}")
                # emit signal for server to pick up changes
                self.delete_user_signal.emit(user)
            self.remove_record.setDisabled(True)
            self.model.select()
            # clear lineEdit texts
            self.clear_text()

        def get_username(self, row: int):
            """ get the username of row number """
            index = self.model.index(row, 1)
            return self.model.data(index)

        def enable_remove_btn(self):
            self.remove_record.setEnabled(True)

        def clear_text(self):
            """ clear input text """
            self.name.clear()
            # self.server_password.clear()
            self.allowed_folder.clear()

        def load_users(self):
            """" emit users as signals for the server to pick up """
            index = self.model.index
            cell = self.model.data
            for i in range(self.model.rowCount()):
                # emit saved users for the server to update
                self.new_user_signal.emit(cell(index(i, 1)), cell(index(i, 2)), cell(index(i, 3)))


if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = ServerSettingsWindow()
    window.show()
    app.exec_()
