import os
import sys
import traceback
sys.path.append(os.path.abspath('src'))
from assistant import assistant_reply
from cost_estimation_module import calculate_cost
from text_embeddings import update_embeddings
from database_connection import DatabaseConnection
from configuration import get_database_credentials_for_environment, get_all_database_credentials
from validation import validate_query
from custom_exceptions import ApplicationException
from formatting import format_query_result
from request_specific_data import Request_data

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
        model = data.get('model')
    except:
        return jsonify({"error": "invalid input"}), 400

    validation_result = validate_query(query, environment, database)
    if not validation_result['is_valid']:
        return jsonify({ "error": validation_result['reason']}), 400

    try:
        db_credentials = get_database_credentials_for_environment(environment)
        db_conn = DatabaseConnection(db_credentials)

        request_data = Request_data(db_conn, database, query, model)
        initial_checkpoint = request_data.get_usage_data()
        response = assistant_reply(request_data)

        response['result'] = format_query_result(response['result'])
        response['cost'] = calculate_cost(request_data, initial_checkpoint)
        db_conn.close()

    except ApplicationException as e:
        print(traceback.format_exc())
        return jsonify({"error": e.message}), 400
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f'unexpected error: {str(e)}'}), 500

    return jsonify(response)

if __name__ == '__main__':
    for db_credentials in get_all_database_credentials():
        db_conn = DatabaseConnection(db_credentials)
        update_embeddings(db_conn)

    app.run(debug=True, port=3000)