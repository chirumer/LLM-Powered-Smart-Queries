import os
import sys
sys.path.append(os.path.abspath('src'))
from sql_query_generation import smart_query
from cost_estimation_module import get_usage_checkpoint, calculate_cost
from text_embeddings import update_embeddings
from database_connection import DatabaseConnection
from configuration import get_database_credentials_for_environment, get_all_database_credentials
from cost_estimation_module import get_usage_checkpoint, calculate_cost
from validation import validate_query
from custom_exceptions import ApplicationException
from formatting import format_query_result

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def handle_query():
    if not request.is_json:
        return jsonify({"error": "expecting JSON"}), 400

    try:
        data = request.get_json()
        query = data.get('query')
        environment = data.get('environment')
        database = data.get('database')
    except:
        return jsonify({"error": "invalid input"}), 400

    validation_result = validate_query(query, environment, database)
    if not validation_result['is_valid']:
        return jsonify({ "error": validation_result['reason']}), 400

    try:
        initial_checkpoint = get_usage_checkpoint()
        db_credentials = get_database_credentials_for_environment(environment)
        db_conn = DatabaseConnection(db_credentials)
        response = smart_query(db_conn, database, query)

        # temporary dummy response
        # response = {
        #     'result': [{'dummy result': 'dummy value'}],
        #     'sql_query': 'SELECT * FROM table WHERE column = value',
        #     'cost': {
        #         'embedding_cost': 0,
        #         'model_cost': 0
        #     }
        # }

        response['result'] = format_query_result(response['result'])
        response['cost'] = calculate_cost(initial_checkpoint, get_usage_checkpoint())
        db_conn.close()

    except ApplicationException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": f'unexpected error: {str(e)}'}), 500

    return jsonify(response)

if __name__ == '__main__':
    for db_credentials in get_all_database_credentials():
        db_conn = DatabaseConnection(db_credentials)
        
        initial_checkpoint = get_usage_checkpoint()
        update_embeddings(db_conn)
        cost = calculate_cost(initial_checkpoint, get_usage_checkpoint())
        print('cost for updating embeddings:', cost['embedding_cost'], sep='')

    app.run(debug=True, port=3000)