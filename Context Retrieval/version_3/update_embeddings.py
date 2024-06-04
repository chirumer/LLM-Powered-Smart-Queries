import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import json
from openai import OpenAI

client = OpenAI()
EMBEDDING_MODEL = "text-embedding-3-small"
LAST_UPDATED_PATH = 'last_updated.json'
EMBEDDINGS_PATH = 'embeddings/'

if not os.path.exists(EMBEDDINGS_PATH):
    os.makedirs(EMBEDDINGS_PATH)

if not os.path.exists(LAST_UPDATED_PATH):
    with open(LAST_UPDATED_PATH, 'w') as f:
        json.dump({}, f)
last_updated_schema = json.load(open(LAST_UPDATED_PATH))

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path='../../.env')

# Retrieve database credentials from environment variables
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')


def create_embedding(data):
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[data])
    embedding = [e.embedding for e in response.data][0]
    return embedding


class DatabaseConnection:
    def __init__(self, eligible_databases):
        self.connection = None
        self.eligible_databases = eligible_databases
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

    def get_all_databases(self):
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

    def get_all_tables(self, db_name):
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
    
    def get_eligible_databases(self):
        return self.eligible_databases

    def get_eligible_tables(self, db_name):
        if db_name == 'hyperface_platform_dev':
            return ['job', 'job_type_config', 'shedlock']
        else:
            return self.get_all_tables(db_name)

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


def update_embeddings(allowed_databases=['grimlock_dev_db', 'hyperface_dev_db', 'hyperface_platform_dev']):
    try:
        db_conn = DatabaseConnection(allowed_databases)
        for db in db_conn.get_eligible_databases():
            for table in db_conn.get_eligible_tables(db):
                text_description = f"The table {table} has the following columns: "
                schema = db_conn.describe_table(db, table)
                for row in schema:
                    row_description = f"{row[0]} of type {row[1]}"
                    if row[2] == 'YES':
                        row_description += " that can be null"
                    else:
                        row_description += " that cannot be null"
                    if row[3] == 'PRI':
                        row_description += " and is a primary key"
                    if row[4]:
                        row_description += f" with a default value of {row[4]}"
                    if row[5]:
                        row_description += f" and has the extra attribute {row[5]}"
                    
                    text_description += "\n" + row_description

                key = '.'.join([db, table])
                if key in last_updated_schema:
                    last_updated = last_updated_schema[key]
                    if last_updated == text_description:
                        continue

                embedding = create_embedding(text_description)
                embedding_path = EMBEDDINGS_PATH + key + '.json'
                with open(embedding_path, 'w') as f:
                    json.dump(embedding, f)

                last_updated_schema[key] = text_description
                with open(LAST_UPDATED_PATH, 'w') as f:
                    json.dump(last_updated_schema, f)
                
                print('updated schema for', key)
    finally:
        db_conn.close()