import pyodbc
from user_credential import user, password

class DatabaseManager:
    def __init__(self):
        #self.username = username
        pass
    def connect(self):
        conn_str = (f"DRIVER={{Client Access ODBC Driver (32-bit)}};"
                    "System=XXX;"
                    "Port=XXX;"
                    f"uid={user};"
                    f"pwd={password};"
                    "Database=XXX;")
        return pyodbc.connect(conn_str)

    def get_data(self, query):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            return columns, rows
        

