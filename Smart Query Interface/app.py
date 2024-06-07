from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql.cursors
import json

app = Flask(__name__, static_folder='static', static_url_path="")
CORS(app)

# Database connection
connection = pymysql.connect(host='localhost',
                             user='cloud',
                             password='scape',
                             database='TextToSql',
                             cursorclass=pymysql.cursors.DictCursor)


environments = ["Hyperface User Acceptance Testing Environment", "Prod"]
databases = {
        "Hyperface User Acceptance Testing Environment": ["Database A", "Database B"],
        "Prod": ["Database X", "Database Y", "Database Z"]
            }

@app.route('/')
def index():
    return send_from_directory("static", "index.html")

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
            sqlQuery = "SELECT * FROM SESSIONS This is a dummy sql query"
            answer_object = {
                "role": "assistant",
                "content": answer,
                "metadata": sqlQuery
            }
            # Update conversation in the database with answer
            updated_conversation.append(answer_object)
            sql = "UPDATE sessions SET conversation = %s WHERE sessionId = %s"
            cursor.execute(sql, (json.dumps(updated_conversation), sessionId))
            connection.commit()

            return jsonify({
                "answer": """<table>
                <thead>
                    <tr>
                        <th>COLUMN_NAME</th>
                        <th>DATA_TYPE</th>
                        <th>IS_NULLABLE</th>
                        <th>COLUMN_KEY</th>
                        <th>COLUMN_DEFAULT</th>
                        <th>EXTRA</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>account_creation_date</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>block_code</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>block_code1</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>block_code2</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>card_block_code</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>card_creation_date</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>card_holder_type</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>card_last_four</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>created_at</td>
                        <td>datetime</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>customer_number</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>first_name</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>id</td>
                        <td>bigint</td>
                        <td>NO</td>
                        <td>PRI</td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>int_status</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>last_updated</td>
                        <td>datetime</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>logo</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>metadata</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>mobile_number</td>
                        <td>varbinary</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>prev_logo</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>relationship_number</td>
                        <td>varchar</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>status</td>
                        <td>enum</td>
                        <td>YES</td>
                        <td></td>
                        <td>None</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>""",
                "metadata": sqlQuery
            }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/environments', methods=['GET'])
def get_environments():
    return jsonify(environments=environments)

@app.route('/api/databases/<environment>', methods=['GET'])
def get_databases(environment):
    if environment in databases:
        return jsonify(databases[environment])
    else:
        return jsonify(error='Environment not found'), 404
    
def get_model_reply(conversation):
    return f"Dummy reply for {conversation[-1]['content']}"

if __name__ == '__main__':
    app.run(debug=True)
