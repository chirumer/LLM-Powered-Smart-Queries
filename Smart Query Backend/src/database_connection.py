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
        self.connection = mysql.connector.connect(
            host=database_credentials.db_host,
            user=database_credentials.db_user,
            password=database_credentials.db_password
        )
        if self.connection.is_connected():
            print("Connected to MySQL server")
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    def get_databases(self):
        cursor = self.connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        cursor.close()
        return [db[0] for db in databases]

    def get_tables(self, db_name):
        cursor = self.connection.cursor()
        cursor.execute(f"USE {db_name}")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        return [table[0] for table in tables]

    def describe_table(self, db_name, table_name):
        cursor = self.connection.cursor()
        cursor.execute(f"USE {db_name}")
        cursor.execute(f"DESCRIBE {table_name}")
        schema = cursor.fetchall()
        cursor.close()
        return schema
    
    def run_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()

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