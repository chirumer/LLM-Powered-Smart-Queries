from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql.cursors
import json
import requests

app = Flask(__name__, static_folder='static', static_url_path="")
CORS(app)

# Database connection
connection = pymysql.connect(host='localhost',
                             user='cloud',
                             password='scape',
                             database='TextToSql',
                             cursorclass=pymysql.cursors.DictCursor)


environments = ["Dev", "Hyperface User Acceptance Testing Environment", "Prod"]
databases = {
    "Dev": ["all", "hyperface_dev_db", "grimlock_dev_db", "hyperface_platform_dev"],
    "Hyperface User Acceptance Testing Environment": ["all", "hyperface_dev_db", "grimlock_dev_db", "hyperface_platform_dev"],
    "Prod": ["all", "hyperface_dev_db", "grimlock_dev_db", "hyperface_platform_dev"]
}
available_models = [
    "openai | gpt-3.5-turbo", 
    "google | gemini-1.5-flash",
    "groq | llama3-70b-8192", 
    "groq | llama3-8b-8192",
    "groq | gemma-7b-it",
    "groq | gemma2-9b-it",
    "groq | mixtral-8x7b-32768",
    "local | mistral-7b"
]

@app.route('/')
def index():
    return send_from_directory("static", "index.html")

@app.route('/api/sessions', methods=['POST'])
def create_session():
    try:
        data = request.json
        Environment = data.get('Environment', None)
        DatabaseName = data.get('DatabaseName', None)
        Model = data.get('Model', None)
        
        with connection.cursor() as cursor:
            sql = "INSERT INTO sessions (conversation, Environment, DatabaseName, session_title, model_name) VALUES (%s, %s, %s, 'New Chat..', %s)"
            cursor.execute(sql, ('[]', Environment, DatabaseName, Model))
            connection.commit()
            sessionId = cursor.lastrowid
            session = {
                "sessionId": str(sessionId),
                "conversation": [],
                "Environment": Environment,
                "DatabaseName": DatabaseName,
                "session_title": "New Chat..",
                "model_name": Model
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

            if len(updated_conversation) == 1:
                # update session title
                sql = "UPDATE sessions SET session_title = %s WHERE sessionId = %s"
                cursor.execute(sql, (question, sessionId))

            answer, sql_query, embedding_cost, model_cost = get_model_reply(updated_conversation, session['databaseName'], session['model_name'])
            metadata = f"SQL Query: {sql_query} | Embedding Cost: {embedding_cost} | Model Cost: {model_cost}"
            
            answer_object = {
                "role": "assistant",
                "content": answer,
                "metadata":metadata
            }
            # Update conversation in the database with answer
            updated_conversation.append(answer_object)
            sql = "UPDATE sessions SET conversation = %s WHERE sessionId = %s"
            cursor.execute(sql, (json.dumps(updated_conversation), sessionId))
            connection.commit()

            

            return jsonify({ "answer": answer,"metadata": metadata }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/environments', methods=['GET'])
def get_environments():
    return jsonify(environments=environments)

@app.route('/api/available_models', methods=['GET'])
def get_available_models():
    return jsonify(available_models=available_models)

@app.route('/api/databases/<environment>', methods=['GET'])
def get_databases(environment):
    if environment in databases:
        return jsonify(databases[environment])
    else:
        return jsonify(error='Environment not found'), 404
    
@app.route('/api/sessions/<string:sessionId>', methods=['DELETE'])
def delete_session(sessionId):
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM sessions WHERE sessionId = %s"
            cursor.execute(sql, (sessionId,))
            connection.commit()
            if cursor.rowcount == 0:
                return jsonify({"error": "Session not found"}), 404
            return jsonify({"message": "Session deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<string:sessionId>/title', methods=['PATCH'])
def update_session_title(sessionId):
    try:
        data = request.json
        new_title = data.get('title')
        
        if not new_title:
            return jsonify({"error": "New title is required"}), 400
        
        with connection.cursor() as cursor:
            sql = "UPDATE sessions SET session_title = %s WHERE sessionId = %s"
            cursor.execute(sql, (new_title, sessionId))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Session not found"}), 404
            
            return jsonify({"success": True, "message": "Title updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def get_model_reply(conversation, database_name, model):
    query = conversation[-1]['content']
    url = "http://localhost:3000/query"
    data = {
        "query": query,
        "environment": "dev",
        "database": database_name,
        "model": model
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            print(response_data)
            return response_data.get('result'), response_data.get('sql_query'), response_data.get('cost').get('embedding_cost'), response_data.get('cost').get('model_cost')
        elif response.status_code == 400 or response.status_code == 500:
            response_data = response.json()
            return response_data.get('error'), None, 0, 0
        else:
            print(f"Error: Received status code {response.status_code}")
            return 'An Internal Server Error Occurred', None, 0, 0
    except requests.RequestException as e:
        print(f"An error occurred: {str(e)}")
        return 'An Internal Server Error Occurred', None, 0, 0

if __name__ == '__main__':
    app.run(debug=True, port=5005)