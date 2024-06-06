import os
import sys
sys.path.append(os.path.abspath('src'))
from sql_query_generation import smart_query
from cost_estimation_module import get_usage_checkpoint, calculate_cost

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def handle_query():
    if not request.is_json:
        return jsonify({"error": "Invalid input"}), 400
    
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({"error": "Query not provided"}), 400

    initial_checkpoint = get_usage_checkpoint()
    response = smart_query(query)
    response['cost'] = calculate_cost(initial_checkpoint, get_usage_checkpoint())
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=3000)