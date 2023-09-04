from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtSql import QSqlQueryModel, QSqlQuery


# sub-class QSqlQueryModel to:
#   set query by default

HEADERS = {"nameId": "Product Name",
           "priceOutId": "Price Sold (Kshs)",
           "quantityId": "Quantity (ml)",
           "commentId": "Comments",
           }


class SalesModel(QSqlQueryModel):
    """ category custom sql query model """

    def __init__(self, category_name: str, db_conn, *args, **kwargs):

        self.category_name = category_name
        self.db_connection = db_conn

        # start query for making sql queries
        self.query = QSqlQuery(db=self.db_connection)

        self.query.prepare(
            "SELECT Names.name, PricesOut.price, Quantities.quantity, Comments.comment FROM Sales "
            "INNER JOIN Names ON Sales.nameId = Names.nameId "
            "INNER JOIN PricesOut ON Sales.priceOutId = PricesOut.priceOutId "
            "INNER JOIN Quantities ON Sales.quantityId = Quantities.quantityId "
            "INNER JOIN Comments ON Sales.commentId = Comments.commentId "
            "INNER JOIN Categories ON Sales.categoryId = Categories.categoryId "
            "WHERE Categories.category LIKE '%' || :category_name || '%' "
        )
        # Sales table: (nameId, priceOutId, quantityId, commentId, categoryId, size, date)
        self.query.addBindValue(":category_name", self.category_name)
        self.query.exec()
        # set query
        self.setQuery(self.query)
