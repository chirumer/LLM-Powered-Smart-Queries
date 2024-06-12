from context_retrieval import select_relevant_tables
from models_wrapper import get_instruct_response
from configuration import CONSTANTS, get_database_credentials_for_environment 
from custom_exceptions import ApplicationException
from validation import is_generated_safe_query

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

def text_to_sql_prompt(request_data):
    relevant_tables = select_relevant_tables(request_data)

    prompt = 'Here are the available table schema:\n'
    for table in relevant_tables:
        schema = request_data.db_conn.describe_table(*table.split('.'))
        prompt += f'{table}:\n'
        prompt += format_schema(schema)
    prompt += '\n'

    prompt += f"Please write the SQL query to solve the following query. Give me JUST the executable query and nothing else, no extra characters either:\n{request_data.query}\n"
    return prompt

def text_to_sql(request_data):
    prompt = text_to_sql_prompt(request_data)
    sql_query = get_instruct_response(prompt, request_data.usage_data)
    return sql_query

def smart_query(request_data):

    failed_queries = []
    tries = 0
    while tries < CONSTANTS.MAX_QUERY_REGENERATION:

        sql_query =  text_to_sql(request_data)
        print('generated SQL query:', sql_query)
        if not is_generated_safe_query(sql_query):
            raise ApplicationException(f"generated unsafe query {sql_query}")
        
        try:
            result = request_data.db_conn.run_query(sql_query)

        except Exception as e:
            failed_queries.append(sql_query)
            tries += 1
            print('failed query', sql_query, e)
            continue

        print('query executed successfully', result)
        return { "sql_query": sql_query, "result": result }

    raise ApplicationException(f"generated but failed to execute queries: {failed_queries}")