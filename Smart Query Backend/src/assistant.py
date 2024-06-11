from sql_query_generation import smart_query
from custom_exceptions import QueryGenerationFail

def assistant_reply(db_conn, database, query):
    # to do: handle conversations

    try:
        response = smart_query(db_conn, database, query)
        return response
    except QueryGenerationFail as e:
        response = {
            'sql_query': None,
            'result': [{ 'query_generation_fail_message': 'The currently selected database cannot be used to answer this query.' }]
        }
        return response
