from context_retrieval import select_relevant_tables
from models_wrapper import get_instruct_response
from configuration import CONSTANTS, get_database_credentials_for_environment 
from custom_exceptions import ApplicationException

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

def text_to_sql_prompt(db_conn, database, query):
    relevant_tables = select_relevant_tables(db_conn, database, query)

    prompt = 'Here are the available table schema:\n'
    for table in relevant_tables:
        schema = db_conn.describe_table(*table.split('.'))
        prompt += f'{table}:\n'
        prompt += format_schema(schema)
    prompt += '\n'

    prompt += f"Please write the SQL query to solve the following query. Give me JUST the executable query and nothing else:\n{query}\n"
    return prompt

def text_to_sql(db_conn, database, query):
    prompt = text_to_sql_prompt(db_conn, database, query)
    sql_query = get_instruct_response(prompt)
    return sql_query

def smart_query(db_conn, environment, database, query):

    failed_queries = []
    tries = 0
    while tries < CONSTANTS.MAX_QUERY_REGENERATION:

        sql_query =  text_to_sql(db_conn, database, query)
        print(sql_query)
        result = db_conn.run_query(sql_query)

        if result == None:
            failed_queries.append(sql_query)
            tries += 1
        else:
            print('success result', result)
            db_conn.close()
            return { "sql_query": sql_query, "result": str(result) }

    db_conn.close()
    raise ApplicationException(f"Generated but failed to execute queries: {failed_queries}")