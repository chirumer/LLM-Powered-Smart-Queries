from database_connection import DatabaseConnection
import os
import json
from models_wrapper import create_embedding


LAST_UPDATED_PATH = 'last_updated.json'
EMBEDDINGS_PATH = 'embeddings/'


if not os.path.exists(EMBEDDINGS_PATH):
    os.makedirs(EMBEDDINGS_PATH)

if not os.path.exists(LAST_UPDATED_PATH):
    with open(LAST_UPDATED_PATH, 'w') as f:
        json.dump({}, f)
last_updated_schema = json.load(open(LAST_UPDATED_PATH))


##### EXPORTS #####

def update_embeddings():
    try:
        db_conn = DatabaseConnection()
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

def get_embeddings(path=EMBEDDINGS_PATH):
    embeds = {}
    for file in os.listdir(path):
        with open(path + file, 'r') as f:
            embeds[file.replace('.json', '')] = json.load(f)
    return embeds