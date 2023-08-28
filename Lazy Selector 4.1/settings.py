from sqlite3 import connect


class Configuration():

    def __init__(self):

        self.__connection = connect(":memory:")
        self.__c = self.__connection.cursor()
        try:
            self.__c.execute(
                """CREATE TABLE config(fg text, bg text, folder text, position text)""")
        except Exception:
            pass

    def update_values(self, fg, bg, folder, position):

        with self.__connection:
            self.__c.execute("""UPDATE config SET (?, ?, ?, ?)""",
                             (fg, bg, folder, position))

    def get_value(self, spec):

        self.__c.execute("""SELECT * FROM config""")
        return self.__c.fetchone()
