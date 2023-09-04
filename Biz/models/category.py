from PyQt6.QtCore import QSortFilterProxyModel
from PyQt6.QtSql import QSqlQueryModel, QSqlQuery


# sub-class QSqlQueryModel to:
#   set query by default

HEADERS = {"nameId": "Product Name",
           "priceInId": "Price Bought (Kshs)",
           "quantityId": "Quantity (ml)",
           "commentId": "Comments",
           }


class CategoryModel(QSqlQueryModel):
    """ category custom sql query model """

    def __init__(self, category_name: str, db_conn, *args, **kwargs):

        self.category_name = category_name
        self.db_connection = db_conn

        # start query for making sql queries
        self.query = QSqlQuery(db=self.db_connection)

        self.query.prepare(
            "SELECT Names.name, PricesIn.price, Quantities.quantity, Comments.comment FROM Stock "
            "INNER JOIN Names ON Stock.nameId = Names.nameId "
            "INNER JOIN PricesIn ON Stock.priceInId = PricesIn.priceInId "
            "INNER JOIN Quantities ON Stock.quantityId = Quantities.quantityId "
            "INNER JOIN Comments ON Stock.commentId = Comments.commentId "
            "INNER JOIN Categories ON Stock.categoryId = Categories.categoryId "
            "WHERE Categories.category LIKE '%' || :category_name || '%' "
        )
        # Stock table: (nameId, priceInId, quantityId, commentId, categoryId, size, date)
        self.query.addBindValue(":category_name", self.category_name)
        self.query.exec()
        # set query
        self.setQuery(self.query)
