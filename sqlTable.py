from PyQt5.QtSql import QSqlQuery
from asfaUtils import get_files, get_folders


def create_data(conn, generators):
    query = QSqlQuery(conn)
    query.exec(
        """
        CREATE TABLE disk (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        name VARCHAR(260) NOT NULL,
        directory VARCHAR(500),
        fileType VARCHAR(12) NOT NULL,
        size VARCHAR(6) NOT NULL
        )
        """)
    # creating a query for later execution using .prepare()
    query.prepare(
        """
        INSERT INTO disk (
            name,
            directory,
            fileType,
            size
            )
            VALUES (?, ?, ?, ?)
        """
    )

    # use .addBindValue() to insert data into the db
    for generator in generators:
        for name, directory, fileType, size in generator:
            query.addBindValue(name)
            query.addBindValue(directory)
            query.addBindValue(fileType)
            query.addBindValue(size)
            query.exec_()


if __name__ == '__main__':
    from PyQt5.QtSql import QSqlDatabase
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    path = "C:\\Users\\code\\Music"

    db = QSqlDatabase.addDatabase("QSQLITE", "file_connection")
    db.setDatabaseName("files.sqlite")
    generators = [get_files(folder) for folder in get_folders(path)]

    if db.open():
        create_data(db, generators)
    app.exec_()
