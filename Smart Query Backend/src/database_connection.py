import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import json

class DatabaseCredentials:
    def __init__(self, db_host, db_user, db_password):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password

class DatabaseConnection:
    def __init__(self, database_credentials):
        self.connection = None
        self.connect(database_credentials)
    
    def connect(self, database_credentials):
        try:
            self.connection = mysql.connector.connect(
                host=database_credentials.db_host,
                user=database_credentials.db_user,
                password=database_credentials.db_password
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
    
    def run_query(self, query):
        if not self.connection or not self.connection.is_connected():
            print("No active MySQL connection")
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()

            column_names = [i[0] for i in cursor.description]

            def process_value(value):
                if isinstance(value, bytes):
                    return "0x" + value.hex().upper()
                return str(value)
            
            json_data = [
                {column: process_value(value) for column, value in zip(column_names, row)}
                for row in result
            ]
            json_result = json.dumps(json_data, indent=4)

            return json_result

        except Error as e:
            print(f"Error: {e}")
            return None
        
        finally:
            cursor.close()