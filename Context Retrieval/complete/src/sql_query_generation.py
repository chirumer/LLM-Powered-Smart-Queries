from context_retrieval import select_relevant_tables
from database_connection import DatabaseConnection
from models_wrapper import get_instruct_response

def format_schema(schema):
    headings = ["Field", "Type", "Null", "Key", "Default", "Extra"]

    schema_string = ''
    head_str = " | ".join(headings) + "\n"
    head_len = len(head_str)
    schema_string += "-" * head_len + "\n"
    schema_string += head_str
    schema_string += "-" * head_len + "\n"
    schema_string += "\n".join([f"{column[0]} | {column[1]} | {column[2]} | {column[3]} | {column[4]} | {column[5]}" for column in schema])
    schema_string += "\n" + "-" * head_len + "\n"
    
    return schema_string

def text_to_sql_prompt(db_conn, query):
    relevant_tables = select_relevant_tables(db_conn, query)

    prompt = 'Here are the available table schema:\n'
    for table in relevant_tables:
        schema = db_conn.describe_table(*table.split('.'))
        prompt += f'{table}:\n'
        prompt += format_schema(schema)
    prompt += '\n'

    prompt += f"Please write the SQL query to solve the following query. Give me JUST the executable query and nothing else:\n{query}\n"
    return prompt

def text_to_sql(db_conn, query):
    prompt = text_to_sql_prompt(db_conn, query)
    response = get_instruct_response(prompt)
    return response.choices[0].text.strip()

def smart_query(query):
    db_conn = DatabaseConnection()

    failed_queries = []
    tries = 0
    while tries < 3:

        sql_query =  text_to_sql(db_conn, query)
        print(sql_query)
        result = db_conn.run_query(sql_query)

        if result == None:
            failed_queries.append(sql_query)
            tries += 1
        else:
            print('success')
            db_conn.close()
            return result

    db_conn.close()
    raise Exception(f"Failed to execute the following queries: {failed_queries}")
