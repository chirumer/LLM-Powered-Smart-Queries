from flask import Flask, request, jsonify,send_from_directory
from flask_cors import CORS
import pymysql.cursors
import json
import requests
app = Flask(__name__,static_folder='static',static_url_path="")
CORS(app)

# Database connection
connection = pymysql.connect(host='localhost',
                             user='cloud',
                             password='scape',
                             database='TextToSql',
                             cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return send_from_directory("static","index.html")

@app.route('/api/sessions', methods=['POST'])
def create_session():
    try:
        data = request.json
        Environment = data.get('Environment', None)
        DatabaseName = data.get('DatabaseName', None)
        
        with connection.cursor() as cursor:
            sql = "INSERT INTO sessions (conversation, Environment, DatabaseName) VALUES (%s, %s, %s)"
            cursor.execute(sql, ('[]', Environment, DatabaseName))
            connection.commit()
            sessionId = cursor.lastrowid
            session = {
                "sessionId": str(sessionId),
                "conversation": [],
                "Environment": Environment,
                "DatabaseName": DatabaseName
            }
            return jsonify(session), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    try:
        with connection.cursor() as cursor:
            # Fetch all sessions from the database
            sql = "SELECT * FROM sessions"
            cursor.execute(sql)
            sessions = cursor.fetchall()
            return jsonify(sessions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<string:sessionId>', methods=['GET'])
def get_session(sessionId):
    try:
        with connection.cursor() as cursor:
            # Fetch session by ID from the database
            sql = "SELECT * FROM sessions WHERE sessionId = %s"
            cursor.execute(sql, (sessionId,))
            session = cursor.fetchone()
            if session is None:
                return jsonify({"error": "Session not found"}), 404
            return jsonify(session)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<string:sessionId>/question', methods=['POST'])
def add_question(sessionId):
    print('testing')
    try:
        with connection.cursor() as cursor:
            # Fetch session by ID from the database
            sql = "SELECT * FROM sessions WHERE sessionId = %s"
            cursor.execute(sql, (sessionId,))
            session = cursor.fetchone()
            if session is None:
                return jsonify({"error": "Session not found"}), 404

            data = request.json
            if not data or 'question' not in data:
                return jsonify({"error": "Invalid request, 'question' key is required"}), 400

            question = data['question']
            question_object = {
                "role": "user",
                "content": question,
            }

            # Update conversation in the database
            conversation = json.loads(session['conversation']) + [question_object]
            sql = "UPDATE sessions SET conversation = %s WHERE sessionId = %s"
            cursor.execute(sql, (json.dumps(conversation), sessionId))
            connection.commit()

            # Retrieve updated conversation from the database
            sql = "SELECT conversation FROM sessions WHERE sessionId = %s"
            cursor.execute(sql, (sessionId,))
            updated_conversation = json.loads(cursor.fetchone()['conversation'])

            print(session['databaseName'])
            answer, sql_query, embedding_cost, model_cost = get_model_reply(updated_conversation, session['databaseName'])
            answer_object = {
                "role": "assistant",
                "content": answer,
                "metadata":sql_query
            }
            # Update conversation in the database with answer
            updated_conversation.append(answer_object)
            sql = "UPDATE sessions SET conversation = %s WHERE sessionId = %s"
            cursor.execute(sql, (json.dumps(updated_conversation), sessionId))
            connection.commit()

            metadata = f"SQL Query: {sql_query};\nEmbedding Cost: {embedding_cost};\nModel Cost: {model_cost}"

            return jsonify({"answer": answer,"metadata":metadata}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_model_reply(conversation, database_name):
    query = conversation[-1]['content']
    url = "http://localhost:3000/query"
    data = {
        "query": query,
        "environment": "dev",
        "database": database_name
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            print(response_data)
            return response_data.get('result'), response_data.get('sql_query'), response_data.get('cost').get('embedding_cost'), response_data.get('cost').get('model_cost')
        else:
            print(f"Error: Received status code {response.status_code}")
            return 'An Internal Server Error Occurred', None, 0, 0
    except requests.RequestException as e:
        print(f"An error occurred: {str(e)}")
        return 'An Internal Server Error Occurred', None, 0, 0

if __name__ == '__main__':
    app.run(debug=True)
