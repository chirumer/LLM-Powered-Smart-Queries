from database_connection import DatabaseConnection
import os
import json
from models_wrapper import create_embedding
from custom_exceptions import ApplicationException
from configuration import filter_databases, filter_tables


LAST_UPDATED_PATH = 'last_updated.json'
EMBEDDINGS_PATH = 'embeddings/'


if not os.path.exists(EMBEDDINGS_PATH):
    os.makedirs(EMBEDDINGS_PATH)

if not os.path.exists(LAST_UPDATED_PATH):
    with open(LAST_UPDATED_PATH, 'w') as f:
        json.dump({}, f)
last_updated_schema = json.load(open(LAST_UPDATED_PATH))


##### EXPORTS #####

def update_embeddings(db_conn):

    for db in filter_databases(db_conn.get_databases()):
        for table in filter_tables(db, db_conn.get_tables(db)):
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

def get_embeddings(database, path=EMBEDDINGS_PATH):
    embeds = {}

    if database == 'all':
        for file in os.listdir(path):
            with open(path + file, 'r') as f:
                embeds[file.replace('.json', '')] = json.load(f)
        return embeds

    for file in os.listdir(path):
        db_name = file.split('.')[0]
        if db_name == database:
            with open(path + file, 'r') as f:
                embeds[file.replace('.json', '')] = json.load(f)
    
    return embeds