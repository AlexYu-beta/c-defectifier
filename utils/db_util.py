import sqlite3


class DBConnection:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def execute(self, sentence, param):
        return self.cursor.execute(sentence, param)

    def get_cursor_value(self):
        return self.cursor.fetchall()
