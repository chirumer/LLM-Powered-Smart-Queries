from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql.cursors
import json 
from smart_query import smart_query

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Database connection
connection = pymysql.connect(host='localhost',
                             user='cloud',
                             password='scape',
                             database='TextToSql',
                             cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/sessions', methods=['POST'])
def create_session():
    try:
        with connection.cursor() as cursor:
            # Insert a new session into the database
            sql = "INSERT INTO sessions (conversation) VALUES ('[]')"
            cursor.execute(sql)
            connection.commit()
            sessionId = cursor.lastrowid
            session = {"sessionId": str(sessionId), "conversation": []}
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

            # Dummy reply
            answer = get_model_reply(updated_conversation)
            answer_object = {
                "role": "assistant",
                "content": answer,
            }
            # Update conversation in the database with answer
            updated_conversation.append(answer_object)
            sql = "UPDATE sessions SET conversation = %s WHERE sessionId = %s"
            cursor.execute(sql, (json.dumps(updated_conversation), sessionId))
            connection.commit()

            return jsonify({"answer": answer}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def get_model_reply(conversation):
    question = conversation[-1]['content']
    response = smart_query(question)

    return response['result']

if __name__ == '__main__':
    app.run(debug=True, port=4000)
