import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')


class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password
            )
            if self.connection.is_connected():
                print("Connected to MySQL server")
        except Error as e:
            print(f"Error: {e}")
            self.connection = None
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def get_databases(self):
        if not self.connection or not self.connection.is_connected():
            print("No active MySQL connection")
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            return [db[0] for db in databases]
        
        except Error as e:
            print(f"Error: {e}")
            return []
        
        finally:
            cursor.close()

    def get_tables(self, db_name):
        if not self.connection or not self.connection.is_connected():
            print("No active MySQL connection")
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {db_name}")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        
        except Error as e:
            print(f"Error: {e}")
            return []
        
        finally:
            cursor.close()

    def describe_table(self, db_name, table_name):
        if not self.connection or not self.connection.is_connected():
            print("No active MySQL connection")
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"USE {db_name}")
            cursor.execute(f"DESCRIBE {table_name}")
            schema = cursor.fetchall()
            return schema
        
        except Error as e:
            print(f"Error: {e}")
            return None
        
        finally:
            cursor.close()